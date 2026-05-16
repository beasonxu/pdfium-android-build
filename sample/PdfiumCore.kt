package com.example.pdfeditor

import android.graphics.Bitmap
import android.graphics.PointF

/**
 * PDFium 核心封装类
 * 对应 pdfium_jni.cpp 里的 JNI 方法
 */
object PdfiumCore {

    init {
        System.loadLibrary("pdfeditor")
        nativeInit()
    }

    // ── Native 方法声明 ───────────────────────────────────────────

    private external fun nativeInit()
    private external fun nativeDestroy()
    private external fun nativeOpenDocument(path: String, password: String?): Long
    private external fun nativeCloseDocument(docPtr: Long)
    private external fun nativeGetPageCount(docPtr: Long): Int
    private external fun nativeOpenPage(docPtr: Long, pageIndex: Int): Long
    private external fun nativeClosePage(pagePtr: Long)
    private external fun nativeGetPageWidth(pagePtr: Long): Int
    private external fun nativeGetPageHeight(pagePtr: Long): Int
    private external fun nativeRenderPage(
        pagePtr: Long, bitmap: Bitmap,
        startX: Int, startY: Int,
        drawSizeW: Int, drawSizeH: Int,
        renderAnnotations: Boolean
    )
    private external fun nativeAddInkAnnotation(
        pagePtr: Long,
        xPoints: FloatArray, yPoints: FloatArray, pointCount: Int,
        color: Int, width: Float
    ): Long
    private external fun nativeAddHighlightAnnotation(
        pagePtr: Long,
        x1: Float, y1: Float, x2: Float, y2: Float
    ): Long
    private external fun nativeSaveDocument(docPtr: Long, savePath: String): Boolean

    // ── 公开 API ──────────────────────────────────────────────────

    /** 打开 PDF 文档，返回文档句柄 */
    fun openDocument(path: String, password: String? = null): Long =
        nativeOpenDocument(path, password)

    /** 关闭文档 */
    fun closeDocument(docPtr: Long) = nativeCloseDocument(docPtr)

    /** 获取页数 */
    fun getPageCount(docPtr: Long): Int = nativeGetPageCount(docPtr)

    /** 打开某页，返回页句柄 */
    fun openPage(docPtr: Long, pageIndex: Int): Long =
        nativeOpenPage(docPtr, pageIndex)

    /** 关闭页面 */
    fun closePage(pagePtr: Long) = nativeClosePage(pagePtr)

    /** 获取页面宽度（pt） */
    fun getPageWidth(pagePtr: Long): Int = nativeGetPageWidth(pagePtr)

    /** 获取页面高度（pt） */
    fun getPageHeight(pagePtr: Long): Int = nativeGetPageHeight(pagePtr)

    /**
     * 渲染页面到 Bitmap
     * @param renderAnnotations 是否渲染批注
     */
    fun renderPage(
        pagePtr: Long,
        bitmap: Bitmap,
        renderAnnotations: Boolean = true
    ) = nativeRenderPage(pagePtr, bitmap, 0, 0, bitmap.width, bitmap.height, renderAnnotations)

    /**
     * 添加手写批注（Ink）
     * @param strokes 手写轨迹（屏幕坐标，会自动转换）
     * @param pageWidth PDF 页面宽度
     * @param pageHeight PDF 页面高度
     * @param screenWidth 屏幕宽度
     * @param screenHeight 屏幕高度
     * @param color 颜色 ARGB（例如 0xFF000000.toInt() 黑色）
     */
    fun addInkAnnotation(
        pagePtr: Long,
        strokes: List<List<PointF>>,
        pageWidth: Int, pageHeight: Int,
        screenWidth: Int, screenHeight: Int,
        color: Int = 0xFF000000.toInt(),
        strokeWidth: Float = 2f
    ) {
        for (stroke in strokes) {
            val pdfPoints = stroke.map {
                screenToPdf(it, screenWidth, screenHeight, pageWidth, pageHeight)
            }
            val xs = pdfPoints.map { it.x }.toFloatArray()
            val ys = pdfPoints.map { it.y }.toFloatArray()
            nativeAddInkAnnotation(pagePtr, xs, ys, pdfPoints.size, color, strokeWidth)
        }
    }

    /**
     * 添加高亮批注
     */
    fun addHighlightAnnotation(
        pagePtr: Long,
        x1: Float, y1: Float, x2: Float, y2: Float
    ) = nativeAddHighlightAnnotation(pagePtr, x1, y1, x2, y2)

    /** 保存文档 */
    fun saveDocument(docPtr: Long, savePath: String): Boolean =
        nativeSaveDocument(docPtr, savePath)

    // ── 坐标转换 ──────────────────────────────────────────────────

    /**
     * 屏幕坐标 → PDF 坐标
     * PDF 坐标系 Y 轴从底部算起，和屏幕相反
     */
    private fun screenToPdf(
        point: PointF,
        screenW: Int, screenH: Int,
        pageW: Int, pageH: Int
    ): PointF {
        val pdfX = point.x / screenW * pageW
        val pdfY = pageH - (point.y / screenH * pageH)
        return PointF(pdfX, pdfY)
    }
}
