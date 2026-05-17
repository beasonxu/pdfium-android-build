import re

with open("BUILD.gn", "r") as f:
    content = f.read()

# 先删掉之前可能加过的 pdfium_shared target
content = re.sub(
    r'\nshared_library\("pdfium_shared"\)\s*\{[^}]*\}\n',
    '\n',
    content,
    flags=re.DOTALL
)

# 核心 patch：把 component("pdfium") 改成 shared_library("pdfium")
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

with open("BUILD.gn", "w") as f:
    f.write(content)

print("BUILD.gn patch done")
