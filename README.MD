pySlice
==========

A 3D model Slicing algorithm, written by Matthew Else in Python. Written, firstly because I need a nice algorithm in Python, and secondly because alternative solutions are all licensed under AGPL, and I need a solution for myself that can be used commercially without releasing source code for everything else.

STL.py was not written by me, however I have modified to better fit what I need.

The code currently only supports the following file formats:
* STL

I plan to possibly support other formats such as OBJ, for example however at the moment STL is fine. It currently cannot generate G-Code, and all it will take is a for loop to generate all of the layers. I cannot guarantee that this code will work 100% of the time, and so far it has only been tested with one STL file, however if you test it successfully or unsuccessfully, let me know in the issues section of Github.

pySlice.py is licensed under the MIT license.
