import os

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

if 'pdfium_shared' not in content:
    content += '''
shared_library("pdfium_shared") {
  deps = [ ":pdfium" ]
  output_name = "pdfium"
  configs -= [ "//build/config/android:hide_all_but_jni_onload" ]
}
'''
    print("Added pdfium_shared target")

with open("BUILD.gn", "w") as f:
    f.write(content)

# 去掉 -z,defs
build_config = "build/config/BUILD.gn"
if os.path.exists(build_config):
    with open(build_config, "r") as f:
        cfg = f.read()
    cfg = cfg.replace('"-Wl,-z,defs"', '#"-Wl,-z,defs"')
    with open(build_config, "w") as f:
        f.write(cfg)
    print("Removed -z,defs")

# 直接修改 stack_trace_android.cc，把 _Unwind_ 实现替换成空实现
trace_file = "base/allocator/partition_allocator/src/partition_alloc/partition_alloc_base/debug/stack_trace_android.cc"
if os.path.exists(trace_file):
    with open(trace_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    for line in lines:
        # 把用到 _Unwind_Backtrace 和 _Unwind_GetIP 的函数体替换成空实现
        if '_Unwind_Backtrace' in line or '_Unwind_GetIP' in line:
            new_lines.append('  // stubbed out\n')
        else:
            new_lines.append(line)

    with open(trace_file, "w") as f:
        f.writelines(new_lines)
    print("Stubbed _Unwind_ calls in stack_trace_android.cc")

print("All patches done")
