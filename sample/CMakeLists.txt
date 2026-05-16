cmake_minimum_required(VERSION 3.22.1)
project("pdfeditor")

# ── 引入预编译的 libpdfium.so ─────────────────────────────────────
add_library(pdfium SHARED IMPORTED)
set_target_properties(pdfium PROPERTIES
    IMPORTED_LOCATION
    ${CMAKE_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libpdfium.so
)

# ── 你自己的 JNI 库 ───────────────────────────────────────────────
add_library(
    pdfeditor
    SHARED
    pdfium_jni.cpp
)

# 头文件目录（从下载的 artifact 里的 include/ 复制过来）
target_include_directories(pdfeditor PRIVATE
    ${CMAKE_SOURCE_DIR}/include
)

# 链接
target_link_libraries(pdfeditor
    pdfium
    android
    jnigraphics   # AndroidBitmap API
    log
)
