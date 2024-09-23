
# Bug Classifier & Gumtree

### Short description
This project tries to find different types of bugs within a project with input in the form of link.
Bugs will be identified for Code, Test and Build for the same.

## Pre-Requisites
#### Bug Classifier
- Python: Any python version >3.0
- Distro: Linux(preferably, Ubuntu >20)
- Git: git commandline support
- Libraries: gitpython and beautifulsoup

#### Gumtree
- Python: Any python version >3.0
- Java: Please set the JAVA_HOME variable in your environment to match the location of your Java installation
- Distro: Linux(preferably, Ubuntu >20)
- Install srcML to enable the srcML backend
- Install cgum to enable the Coccinelle backend
- Install pythonparser to enable the Parso backend
- Install jsparser to enable the Acorn backend
- Install tree-sitter-parser to enable the tree-sitter backend

All these external tools have to be available in your system's path.

## Installation Instruction
#### Bug Classifier
- Clone the project:
    git clone https://github.com/CI-Bugs/bug_classifier.git
- Change directory:
    cd bug_classifier
- Check if gitpython module is installed or not:
    pip install gitpython

#### Gumtree
##### Install from release
- You can download a release of GumTree directly on GitHub. Unzip the file and you will find gumtree's binaries in the bin folder

##### Install from sources
- You can build GumTree with the following commands:
    git clone https://github.com/GumTreeDiff/gumtree.git
- cd gumtree
- ./gradlew build

You will have a zip distribution of GumTree in the dist/build/distributions folder. The gumtree binary is located in the bin folder contained in this archive

Also, if you want this binary path to be avilable irrespective of the current working directory please set it to PATH environmanet variable for Linux or Windows

## Run the project:
#### Bug Classifier
-   python DifferenceFinder.py <id> <filepath having links>
    Example1: python DifferenceFinder.py 1 Commit_Links/code.txt
    Example2: python DifferenceFinder.py 2 Commit_Links/test.txt
    Example3: python DifferenceFinder.py 3 Commit_Links/build.txt

#### Gumtree
-   python main.py <source java filepath> <target java filepath>
    Example: python main.py source.java path target.java path
 
 


