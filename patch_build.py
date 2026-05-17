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

# 整个文件替换成空实现，彻底避免 _Unwind_ 依赖
trace_file = "base/allocator/partition_allocator/src/partition_alloc/partition_alloc_base/debug/stack_trace_android.cc"
if os.path.exists(trace_file):
    stub = '''// Copyright 2024 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Stubbed out to avoid _Unwind_ dependency when building as shared library.

#include "partition_alloc/partition_alloc_base/debug/stack_trace.h"

namespace partition_alloc::internal::base::debug {

bool CollectStackTrace(const void** trace, size_t count) {
  return false;
}

}  // namespace partition_alloc::internal::base::debug
'''
    with open(trace_file, "w") as f:
        f.write(stub)
    print("Replaced stack_trace_android.cc with stub")

print("All patches done")
