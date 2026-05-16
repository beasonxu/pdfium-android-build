#include <jni.h>
#include <android/log.h>
#include <string>
#include <vector>

#include "include/fpdfview.h"
#include "include/fpdf_annot.h"
#include "include/fpdf_edit.h"
#include "include/fpdf_save.h"
#include "include/fpdf_text.h"

#define LOG_TAG "PDFiumJNI"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

// ── 初始化 / 释放 ─────────────────────────────────────────────────

extern "C" JNIEXPORT void JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeInit(JNIEnv *env, jclass) {
    FPDF_InitLibrary();
    LOGI("PDFium initialized");
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeDestroy(JNIEnv *env, jclass) {
    FPDF_DestroyLibrary();
}

// ── 文档操作 ──────────────────────────────────────────────────────

extern "C" JNIEXPORT jlong JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeOpenDocument(
        JNIEnv *env, jclass, jstring path, jstring password) {

    const char *filePath = env->GetStringUTFChars(path, nullptr);
    const char *pass = password ? env->GetStringUTFChars(password, nullptr) : nullptr;

    FPDF_DOCUMENT doc = FPDF_LoadDocument(filePath, pass);

    env->ReleaseStringUTFChars(path, filePath);
    if (pass) env->ReleaseStringUTFChars(password, pass);

    if (!doc) {
        LOGE("Failed to open document: %lu", FPDF_GetLastError());
        return 0;
    }
    return reinterpret_cast<jlong>(doc);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeCloseDocument(
        JNIEnv *env, jclass, jlong docPtr) {
    FPDF_CloseDocument(reinterpret_cast<FPDF_DOCUMENT>(docPtr));
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeGetPageCount(
        JNIEnv *env, jclass, jlong docPtr) {
    return FPDF_GetPageCount(reinterpret_cast<FPDF_DOCUMENT>(docPtr));
}

// ── 页面操作 ──────────────────────────────────────────────────────

extern "C" JNIEXPORT jlong JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeOpenPage(
        JNIEnv *env, jclass, jlong docPtr, jint pageIndex) {
    FPDF_PAGE page = FPDF_LoadPage(reinterpret_cast<FPDF_DOCUMENT>(docPtr), pageIndex);
    if (!page) LOGE("Failed to open page %d", pageIndex);
    return reinterpret_cast<jlong>(page);
}

extern "C" JNIEXPORT void JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeClosePage(
        JNIEnv *env, jclass, jlong pagePtr) {
    FPDF_ClosePage(reinterpret_cast<FPDF_PAGE>(pagePtr));
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeGetPageWidth(
        JNIEnv *env, jclass, jlong pagePtr) {
    return (jint) FPDF_GetPageWidth(reinterpret_cast<FPDF_PAGE>(pagePtr));
}

extern "C" JNIEXPORT jint JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeGetPageHeight(
        JNIEnv *env, jclass, jlong pagePtr) {
    return (jint) FPDF_GetPageHeight(reinterpret_cast<FPDF_PAGE>(pagePtr));
}

// ── 渲染到 Bitmap ─────────────────────────────────────────────────

extern "C" JNIEXPORT void JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeRenderPage(
        JNIEnv *env, jclass,
        jlong pagePtr,
        jobject bitmap,
        jint startX, jint startY,
        jint drawSizeW, jint drawSizeH,
        jboolean renderAnnotations) {

    AndroidBitmapInfo info;
    AndroidBitmap_getInfo(env, bitmap, &info);

    void *addr;
    AndroidBitmap_lockPixels(env, bitmap, &addr);

    FPDF_BITMAP fpdfBitmap = FPDFBitmap_CreateEx(
            info.width, info.height, FPDFBitmap_BGRA, addr, info.stride);

    FPDFBitmap_FillRect(fpdfBitmap, 0, 0, info.width, info.height, 0xFFFFFFFF);

    int flags = FPDF_REVERSE_BYTE_ORDER;
    if (renderAnnotations) flags |= FPDF_ANNOT;

    FPDF_RenderPageBitmap(
            fpdfBitmap,
            reinterpret_cast<FPDF_PAGE>(pagePtr),
            startX, startY, drawSizeW, drawSizeH,
            0, flags);

    FPDFBitmap_Destroy(fpdfBitmap);
    AndroidBitmap_unlockPixels(env, bitmap);
}

// ── 手写批注（Ink Annotation）────────────────────────────────────

extern "C" JNIEXPORT jlong JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeAddInkAnnotation(
        JNIEnv *env, jclass,
        jlong pagePtr,
        jfloatArray xPoints,
        jfloatArray yPoints,
        jint pointCount,
        jint color,   // ARGB
        jfloat width) {

    FPDF_PAGE page = reinterpret_cast<FPDF_PAGE>(pagePtr);
    FPDF_ANNOTATION annot = FPDFPage_CreateAnnot(page, FPDF_ANNOT_INK);
    if (!annot) return 0;

    jfloat *xs = env->GetFloatArrayElements(xPoints, nullptr);
    jfloat *ys = env->GetFloatArrayElements(yPoints, nullptr);

    std::vector<FS_POINTF> points(pointCount);
    for (int i = 0; i < pointCount; i++) {
        points[i] = {xs[i], ys[i]};
    }

    FPDFAnnot_AddInkStroke(annot, points.data(), pointCount);

    // 解析颜色 ARGB
    unsigned int a = (color >> 24) & 0xFF;
    unsigned int r = (color >> 16) & 0xFF;
    unsigned int g = (color >> 8)  & 0xFF;
    unsigned int b =  color        & 0xFF;
    FPDFAnnot_SetColor(annot, FPDFANNOT_COLORTYPE_Color, r, g, b, a);

    env->ReleaseFloatArrayElements(xPoints, xs, 0);
    env->ReleaseFloatArrayElements(yPoints, ys, 0);
    FPDFPage_CloseAnnot(annot);

    return 1;
}

// ── 高亮批注 ─────────────────────────────────────────────────────

extern "C" JNIEXPORT jlong JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeAddHighlightAnnotation(
        JNIEnv *env, jclass,
        jlong pagePtr,
        jfloat x1, jfloat y1,
        jfloat x2, jfloat y2) {

    FPDF_PAGE page = reinterpret_cast<FPDF_PAGE>(pagePtr);
    FPDF_ANNOTATION annot = FPDFPage_CreateAnnot(page, FPDF_ANNOT_HIGHLIGHT);
    if (!annot) return 0;

    FS_QUADPOINTSF quad;
    quad.x1 = x1; quad.y1 = y2;
    quad.x2 = x2; quad.y2 = y2;
    quad.x3 = x1; quad.y3 = y1;
    quad.x4 = x2; quad.y4 = y1;
    FPDFAnnot_AppendAttachmentPoints(annot, &quad);

    // 黄色半透明
    FPDFAnnot_SetColor(annot, FPDFANNOT_COLORTYPE_Color, 255, 255, 0, 128);

    FPDFPage_CloseAnnot(annot);
    return 1;
}

// ── 保存文档 ─────────────────────────────────────────────────────

struct FileWriteContext {
    FILE *file;
};

static int FileWriteBlock(FPDF_FILEWRITE *pFileWrite, const void *data, unsigned long size) {
    auto *ctx = reinterpret_cast<FileWriteContext *>(pFileWrite);
    return fwrite(data, 1, size, ctx->file) == size ? 1 : 0;
}

extern "C" JNIEXPORT jboolean JNICALL
Java_com_example_pdfeditor_PdfiumCore_nativeSaveDocument(
        JNIEnv *env, jclass,
        jlong docPtr, jstring savePath) {

    const char *path = env->GetStringUTFChars(savePath, nullptr);
    FILE *file = fopen(path, "wb");
    env->ReleaseStringUTFChars(savePath, path);

    if (!file) {
        LOGE("Failed to open output file");
        return JNI_FALSE;
    }

    FileWriteContext ctx{file};
    FPDF_FILEWRITE fileWrite;
    fileWrite.version = 1;
    fileWrite.WriteBlock = FileWriteBlock;

    jboolean result = FPDF_SaveAsCopy(
            reinterpret_cast<FPDF_DOCUMENT>(docPtr),
            reinterpret_cast<FPDF_FILEWRITE *>(&ctx),
            FPDF_NO_INCREMENTAL);

    fclose(file);
    return result;
}
