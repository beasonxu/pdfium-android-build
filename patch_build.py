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

# -z,defs 를 build/config/BUILD.gn 에서 제거
import os
build_config = "build/config/BUILD.gn"
if os.path.exists(build_config):
    with open(build_config, "r") as f:
        cfg = f.read()
    cfg = cfg.replace('"-Wl,-z,defs"', '#"-Wl,-z,defs"')
    with open(build_config, "w") as f:
        f.write(cfg)
    print("Removed -z,defs from build/config/BUILD.gn")

# stack_trace_android.cc 에서 _Unwind_ 호출 제거
trace_file = "base/allocator/partition_allocator/src/partition_alloc/partition_alloc_base/debug/stack_trace_android.cc"
if os.path.exists(trace_file):
    with open(trace_file, "r") as f:
        trace = f.read()
    # _Unwind_ 함수 호출을 stub으로 교체
    trace = '#define _Unwind_Backtrace(x,y) 0\n#define _Unwind_GetIP(x) 0\n' + trace
    with open(trace_file, "w") as f:
        f.write(trace)
    print("Stubbed _Unwind_ calls in stack_trace_android.cc")

print("All patches done")
