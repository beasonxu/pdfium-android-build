import re

with open("BUILD.gn", "r") as f:
    content = f.read()

# 核心 patch：把 component("pdfium") 改成 shared_library("pdfium")
# 这是 bblanchon/pdfium-binaries 的做法
if 'shared_library("pdfium")' not in content:
    content = content.replace(
        'component("pdfium")',
        'shared_library("pdfium")'
    )
    print("Changed component to shared_library")

# 加 fvisibility=default 和 FPDFSDK_EXPORTS
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

# 去掉我们之前加的 pdfium_shared target（如果有）
content = re.sub(
    r'\nshared_library\("pdfium_shared"\).*?\}\n',
    '',
    content,
    flags=re.DOTALL
)

with open("BUILD.gn", "w") as f:
    f.write(content)

print("BUILD.gn patch done")
