# REAL_STATE_QA - Real State Question&Answer 

<div style="text-align:center"><img width="50%" src="./img/Real-Estate.jpg" /></div>

<div id="top"></div>

<!-- TOC -->
<details open=true>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#coding">Coding</a></li>
        <li><a href="#testing">Testing</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>
<!-- /TOC -->


<!-- ABOUT -->
## **About the Library**
------------------------

This repository aims to query an SQL database, containing Real State information, using natural language in order to obtain the results. This will be done using LLM to create the queries and pass them to the database

<!-- <center>

<img src="img/avutils.png" alt="drawing" width="500"/>

</center>


<p align="right"><a href="#top">Back to top</a></p> -->


<!-- START -->
## **Getting Started**
-----------------------
In order to run the app, run the script launch_app.py

### **Installation**
-------------------
In order to make use of the library, one should just follow the next steps:

1. Clone the project and install it using:
```bash
   git clone <repo-url>
```

2. Install the repository:
```bash
  pip install -e .
```

3. For using llama-cpp-python library using GPU follow the instructions at  [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)

4. Rename the config template for the SQL database at config from mysql-template.yaml to mysql.yaml and configure your database.

5. The llm model is configured using the file at models/cfg.

6. Web APP Login users can be set in the file located at config/login.yaml


<p align="right"><a href="#top">Back to top</a></p>

### **Coding**
-------------------

**When coding, just try to follow the PEP8 style and PEP257 numpy/sphinx notation for docstrings. Any code optimisations are greatly appreciated.**

<p align="right"><a href="#top">Back to top</a></p>

### **Tests**
-------------------

<p align="right"><a href="#top">Back to top</a></p>


<!-- CONTRIBUTING -->
## **Contributing**
--------------------

Any contributions are greatly appreciated. If you have suggestions that would make the project any better, don't hesitate to contribute. Here is a reminder of the steps:

1. Clone the repository:
```bash
  git clone <repo-url>
```
2. Create your branch:
```bash
  git checkout -b branchname
```
3. Implement and test your features.
4. Add changes:
```bash
  git add <files-to-add>
```
5. Commit your changes:
```bash
  git commit -m "<feature-description>"
```
6. Push to the branch: 
```bash
  git push origin branchname
```
7. Request a merge when you are ready.


<p align="right"><a href="#top">Back to top</a></p>
<!-- /CONTRIBUTING -->


<!-- ACKNOWL -->
## **Acknowledgements**
-----------------------

**Enjoy the content!** 😄

<p align="right"><a href="#top">Back to top</a></p>
<!-- /ACKNOWL -->
