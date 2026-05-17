import re

with open("BUILD.gn", "r") as f:
    content = f.read()

# 删掉之前可能加过的 pdfium_shared target
content = re.sub(
    r'\nshared_library\("pdfium_shared"\)\s*\{[^}]*\}\n',
    '\n',
    content,
    flags=re.DOTALL
)

# 把 component("pdfium") 改成 shared_library("pdfium")
if 'shared_library("pdfium")' not in content:
    content = content.replace(
        'component("pdfium")',
        'shared_library("pdfium")'
    )
    print("Changed component to shared_library")

# 加 fvisibility=default
if 'fvisibility=default' not in content:
    content = content.replace(
        'config("pdfium_common_config") {',
        'config("pdfium_common_config") {\n  cflags = [ "-fvisibility=default" ]'
    )
    print("Added fvisibility=default")

# 加 FPDFSDK_EXPORTS
if 'FPDFSDK_EXPORTS' not in content:
    content = content.replace(
        '"PNG_USE_READ_MACROS",',
        '"PNG_USE_READ_MACROS",\n    "FPDFSDK_EXPORTS",'
    )
    print("Added FPDFSDK_EXPORTS")

# 关键：在 shared_library("pdfium") 里去掉 hide_all_but_jni_onload
# 找到 shared_library("pdfium") 块，加入 configs -= 行
if 'hide_all_but_jni_onload' not in content:
    content = content.replace(
        'shared_library("pdfium") {',
        'shared_library("pdfium") {\n  configs -= [ "//build/config/android:hide_all_but_jni_onload" ]'
    )
    print("Removed hide_all_but_jni_onload")

with open("BUILD.gn", "w") as f:
    f.write(content)

print("BUILD.gn patch done")
