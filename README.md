# ReferenceWizard
A tool that converts NuGet package lib references to project references in a Visual Studio solution.

We have a private NuGet repository, where internal components are packaged and published, and later
used throughout the company projects. Sometimes we need to debug those components to solve issues
that were reported during integration. This is a command-line tool that receives the source folder
for libs that are published to NuGet, along with the path to the sln file where those libs are
consumed. The tool attaches the lib projects to the solution, and then replaces lib references with
project references.

## How to use

The main script is wizard.py. It receives path to the directory where your NuGet lib sources are
located as the first argument. The second argument is the path to the target sln file.

`wizard.py C:\PathToYourNuGetLibSources C:\PathToYourTargetSlnFile`
