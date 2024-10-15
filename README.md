
# Bug Classifier & Gumtree

We have collected program and test bugs from the BUGSWARM dataset and use this data to train machine learning models capable of accurately classifying bugs into their respective categories. This project is divided into three main parts:

#### Bugs Discovery
In this phase, we collect build reports from BUGSWARM and extract the buggy commits that caused the build failures.

#### Data Processing
Once the buggy commits are identified, we extract their parent (pre-buggy) commits and compare both versions to generate the AST (Abstract Syntax Tree) for the differential code changes.

#### Bug Classifier
Using the insights derived from the AST reports, we train machine learning models and evaluate their effectiveness in classifying bugs as either program bugs or test bugs.

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

## How to execute the project:
#### Data Discovery
- Execute the Extract_CommitLinks_From_ExportLog.py with appropriate path in the script where the json files from Bugswarm are copied

#### Data Proceessing
-   python DifferenceFinder.py <id> <filepath having links>
    Example1: python DifferenceFinder.py 1 Commit_Links/code.txt
    Example2: python DifferenceFinder.py 2 Commit_Links/test.txt


    ##### Gumtree
    -   python main.py <source java filepath> <target java filepath>
        Example: python main.py source.java path target.java path
 
 
#### Bug Classifier
- Execute the svm_10_avg_90_10.py and svm_N-1.py with appropriate path in the script where the AST files from Data processing are copied


