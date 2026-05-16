# PDFium Android Builder

基于 [Chromium 官方 PDFium](https://pdfium.googlesource.com/pdfium/) 源码，通过 GitHub Actions 自动编译 Android `.so` 库。

## 支持架构

| ABI | 对应设备 |
|-----|---------|
| `arm64` | 现代 64 位 Android 设备（主流） |
| `arm` | 旧版 32 位 Android 设备 |
| `x86_64` | Android 模拟器（64位） |
| `x86` | Android 模拟器（32位） |

---

## 使用方法

### 1. 触发编译

**自动触发**：push 到 `main` 分支时自动编译全部架构。

**手动触发**：
1. 进入 GitHub 仓库 → Actions
2. 选择 `Build PDFium for Android`
3. 点击 `Run workflow`
4. 选择目标架构（默认编译全部）

### 2. 下载产物

编译完成后在 Actions → 对应 workflow run → Artifacts 里下载：

```
libpdfium-android-arm64/
├── libpdfium.so      ← 主库
└── include/          ← 头文件
    ├── fpdfview.h
    ├── fpdf_annot.h
    ├── fpdf_edit.h
    └── ...
```

### 3. 集成到 Android 项目

**放置文件：**
```
app/src/main/
├── jniLibs/
│   ├── arm64-v8a/
│   │   └── libpdfium.so
│   ├── armeabi-v7a/
│   │   └── libpdfium.so
│   ├── x86_64/
│   │   └── libpdfium.so
│   └── x86/
│       └── libpdfium.so
└── cpp/
    ├── CMakeLists.txt
    ├── pdfium_jni.cpp
    └── include/          ← 把下载的头文件放这里
```

**CMakeLists.txt：**
```cmake
cmake_minimum_required(VERSION 3.22.1)
project("pdfeditor")

add_library(pdfium SHARED IMPORTED)
set_target_properties(pdfium PROPERTIES
    IMPORTED_LOCATION
    ${CMAKE_SOURCE_DIR}/../jniLibs/${ANDROID_ABI}/libpdfium.so
)

add_library(pdfeditor SHARED pdfium_jni.cpp)
target_include_directories(pdfeditor PRIVATE ${CMAKE_SOURCE_DIR}/include)
target_link_libraries(pdfeditor pdfium android log)
```

**build.gradle：**
```groovy
android {
    defaultConfig {
        ndk {
            abiFilters 'arm64-v8a', 'armeabi-v7a'
        }
    }
    externalNativeBuild {
        cmake {
            path "src/main/cpp/CMakeLists.txt"
        }
    }
}
```

---

## 编译参数说明

| 参数 | 值 | 说明 |
|------|----|------|
| `pdf_enable_v8` | false | 关闭 JS 引擎，减小体积 |
| `pdf_enable_xfa` | false | 关闭 XFA 表单支持 |
| `pdf_is_standalone` | true | 编译为独立 .so |
| `is_debug` | false | Release 模式 |

---

## 常见问题

**Q: 编译失败怎么办？**
进入 Actions 查看详细日志，常见原因是网络问题导致 gclient sync 失败，重新触发一次即可。

**Q: 多久编译一次？**
每次 push 到 main 自动触发。也可以手动触发。

**Q: 产物保留多久？**
30 天，可在 workflow 文件里修改 `retention-days`。
