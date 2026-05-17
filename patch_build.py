with open("BUILD.gn", "r") as f:
    content = f.read()

if 'fvisibility=default' not in content:
    content = content.replace(
        'config("pdfium_common_config") {',
        'config("pdfium_common_config") {\n  cflags = [ "-fvisibility=default" ]'
    )
    print("Added fvisibility=default")

if 'FPDFSDK_EXPORTS' not in content:
    content = content.replace(
        '"PNG_USE_READ_MACROS",',
        '"PNG_USE_READ_MACROS",\n    "FPDFSDK_EXPORTS",'
    )
    print("Added FPDFSDK_EXPORTS")

# 添加 shared_library target
# 用 allow_undefined_symbols 跳过 _Unwind_ 符号检查
if 'pdfium_shared' not in content:
    content += '''
shared_library("pdfium_shared") {
  deps = [ ":pdfium" ]
  output_name = "pdfium"
  configs -= [ "//build/config/android:hide_all_but_jni_onload" ]
  # 允许未定义符号，避免 _Unwind_ 链接错误
  ldflags = [ "-Wl,--allow-shlib-undefined" ]
}
'''
    print("Added pdfium_shared target")

with open("BUILD.gn", "w") as f:
    f.write(content)

print("BUILD.gn patch done")
