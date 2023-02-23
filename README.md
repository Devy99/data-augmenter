<a name="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Data Augmenter</h3>

  <p align="center">
    A tool for augmenting code and textual data
    <br />
    <a href="https://github.com/Devy99/data-augmenter/issues">Report Bug</a>
    ·
    <a href="https://github.com/Devy99/data-augmenter/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#tool-references">Tool references</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Data Augmenter is a tool that increases the size of a text dataset using a <a href="#tool-references">set of rules</a> that preserves the semantics. Actually, it accepts sentences written in natural language (English) and Java code.



Our goal is to provide a scalable tool to efficiently manage dataset of large dimensions. For this purpose, it is possible to run the tool with a specific number of threads, each of which will compute a chunk of the dataset at a time, thus avoiding to load all of the data into memory.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started
Below is a quick guide to using the tool to augment your datasets.


### Prerequisites

The tool is entirely written in Python, however, it uses several JAR files as subroutines for code transformation rules. Therefore, below are the requirements to run the tool:
* Python (tested on version 3.10.0)
* Java 11

Alternatively, you can use a containerized version of the tool by installing:
* Docker (tested on version 20.10.5)


### Installation

- Clone the repo
   ```sh
   git clone https://github.com/Devy99/data-augmenter
   ```

#### Option 1
- Install Python packages
   ```sh
   pip install -r requirements.txt
   ```

#### Option 2
- Build the Docker image of the tool
   ```sh
   docker build . -t data-augmenter
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage
Before proceeding to use the tool, you must set the config.yaml file based on your needs. 
In particular, choose the branch to configure based on the type of dataset you want to augment ( dataset containing only 'text', one containing only 'code', or one that has both 'text-code'). In the case of 'text-code', the properties will be inherited from the 'text' and 'code' branches except for the maximum number of outputs per pair.

Specifically:

**data-column**: refers to the number of the column where the information to be augmented can be found in the dataset (starts from 0).

**max-outputs**: indicates the maximum number of outputs that the tool should return for each data item. In the scenario where there are multiple variants for that data, a random subset of them will be chosen. If the value is less than 1, all possible outputs will be considered.

**outputs-per-rule**: the maximum number of outputs allowed for each rule. If the value is less than 1, all possible outputs will be considered (we recommend entering a very large number rather than this value).

**active-rules**: the transformation rules to be applied to each data item.

Below is an example configuration for the dataset type with only text data:
```yaml
        text:
          data-column: 1
          max-outputs: 100 
          outputs-per-rule: 5 
          active-rules: [
              "americanize_britishize_english",
              "casual_to_formal",
              "contraction_expansions",
              "discourse_marker_substitution",
              "formal_to_casual",
              "insert_abbreviation",
              "multilingual_back_translation",
              "neural_question_paraphraser",
              "number_to_word",
              "style_paraphraser"
          ]
```

Next, you can launch the script with the commands described below.

```sh
usage: data_augmenter.py [-h] [--output-filepath FILEPATH] [--workers N_WORKERS] [--chunk-size C_SIZE] [--verbose] --input-file FILEPATH --type TYPE

Augment text and code data from CSV file

REQUIRED ARGUMENTS:
--input-file FILEPATH, -i FILEPATH
The CSV filepath where to retrieve the data to augment.

--type TYPE, -t TYPE  
Select the type of augmentation to perform. Possible
choices: 'text', 'code' or 'text-code'

OPTIONAL ARGUMENTS:
--output-filepath FILEPATH, -o FILEPATH
Output filepath where to store the CSV file

--workers N_WORKERS, -w N_WORKERS
Number of threads to be used during the process. Default value = 1

--chunk-size C_SIZE, -cs C_SIZE
Size of the portion of the dataset to be processed by each thread. Default value = 1

--verbose, -v         
If selected it shows some code execution messages on the screen

```

In case you want to use the containerized version of the tool, you can use the previously built image as below. In addition to the tool parameters listed above, you must specify a volume shared with the container containing the dataset to be augmented (and where to create the output dataset). 
```sh
docker run --rm -e PYTHONUNBUFFERED='1' \
            -v /your/path:/container/path data-augmenter \
            -i ./container/path/dataset.csv \
            -o ./container/path/output.csv \
            -t code \
            -w 50 -cs 5
```

or, after updating the volume with the desired path, with docker compose (in this case you have to update the image every time the configuration file is updated):
```sh
docker-compose run --rm data-augmenter \
                    -i /output/dataset.csv \
                    -o /output/dataset_aug.csv \
                    -t code \
                    -w 50 -cs 5 \
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- TOOL REFERENCES -->
## Tool references
<a name="tool-references"></a>
Below we list the tools that were used in this project to apply transformations to the data.

* [NL-Augmenter](https://github.com/GEM-benchmark/NL-Augmenter)
* [Java Transformer](https://github.com/mdrafiqulrabin/JavaTransformer)
* [SPAT (Semantic-and-Naturalness Preserving Auto Transformation)](https://github.com/Santiago-Yu/SPAT)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


