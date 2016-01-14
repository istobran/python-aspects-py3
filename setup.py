from distutils.core import setup
import aspects
setup(name="python-aspects",
      version=".".join(str(s) for s in aspects.version_info),
      description="Lightweight AOP extension",
      author="Antti Kervinen",
      author_email="ask@cs.tut.fi",
      url="http://www.cs.tut.fi/~ask/aspects/index.html",
      py_modules=["aspects"])
