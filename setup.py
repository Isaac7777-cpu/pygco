"""Packaging for the em-yu/pygco layout and its label-cost bindings.

Place beside pygco.py, cgco.py, cgco.cpp, and gco_source/.
GCO sources must already be present (run `make download` if necessary).
No Makefile invocation or network download occurs during installation.
"""

import sys
from glob import glob
from pathlib import Path

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


GCO_SOURCES = [
    "gco_source/graph.cpp",
    "gco_source/maxflow.cpp",
    "gco_source/LinkedBlockList.cpp",
    "gco_source/GCoptimization.cpp",
    "cgco.cpp",
]


class BuildCtypesLibrary(build_ext):
    """Build a ctypes library with the exact filename used by cgco.py.

    This is a shared C++ library, not an importable Python extension. Keeping
    libcgco.so beside the two Python modules lets the original ctypes loader
    work in both editable installs and installed wheels, including on macOS.
    """

    def get_ext_filename(self, ext_name):
        if ext_name == "libcgco":
            return "libcgco.so"
        return super().get_ext_filename(ext_name)

    def run(self):
        if sys.platform == "win32":
            raise RuntimeError("This installer supports Linux and macOS; Windows needs DLL export changes.")
        missing = [path for path in GCO_SOURCES if not Path(path).is_file()]
        missing += [path for path in ("gco_source/GCoptimization.h", "pygco.py", "cgco.py")
                    if not Path(path).is_file()]
        if missing:
            raise RuntimeError(
                "Missing pygco/GCO sources: " + ", ".join(missing)
                + ". Place these packaging files in the fork root and run `make download` if GCO sources are absent."
            )
        super().run()


setup(
    name="pygco-labelcost",
    version="0.1.0",
    description="Python ctypes bindings for GCO with active-label costs",
    python_requires=">=3.8",
    install_requires=["numpy>=1.24.4,<2"],
    py_modules=["pygco", "cgco"],
    ext_modules=[
        Extension(
            "libcgco",
            sources=GCO_SOURCES,
            # Include headers in source distributions as well as builds.
            depends=sorted(glob("gco_source/*.h") + glob("cgco.h")),
            include_dirs=[".", "gco_source"],
            define_macros=[("GCO_MAX_ENERGYTERM", "1000000000")],
            extra_compile_args=["-O3", "-fPIC"],
            language="c++",
        )
    ],
    cmdclass={"build_ext": BuildCtypesLibrary},
    zip_safe=False,
)
