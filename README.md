# Legal Documents Redaction
This repository is for offline semi-automatic data redaction of legal documents by masking named entities identified using Machine Learning. The output of redaction using this code needs to be reviewed by humans to make sure all the sensitive information is masked.


#  1. About Legal Documents Redaction
## Why offline data redaction?
Many a times the legal documents cant be shared outside the organization, even to cloud service providers. So this repository puts the open source AI models togehter in a docker image which can run offline within an organization.

## What is Redaction and why is it important to do this semi-automatically?
Redaction is the process of removing sensitive information from a document. It is important to redact documents to protect sensitive information from being exposed. Sensitive information includes, but is not limited to, personally identifiable information (PII), protected health information (PHI), and financial information.
Doing the redaction manually is time consuming and error prone. This repository provides a semi-automatic way of redacting documents. Since automatic redaction cant remove all the sensitive information, it is important to review the redacted documents to make sure all the sensitive information is masked.

## What information is automatically redacted using this repository?
Information to be redacted is handled in two ways: Masking and Dummy Replacement. In masking, sensitive information is replaced with "XXXX". In dummy replacement, the sensitive information is replaced with dummy information. For example, a company name "Apple Inc." can be replaced with "ORG1" etc. All the company names that are very similar e.g. "Apple" are also replaced with "ORG1".

Following entities in the input documents are identified and redacted using this repository:

| Redaction Type    | Entity Types                                   |
|-------------------|------------------------------------------------|
| Masking           | "DATE", "MONEY", "PERCENT", "QUANTITY", "TIME" |
| Dummy Replacement | "ORG", "PERSON", "PRODUCT"                     |

E.g. Input sentence: "Vodafone is engaged in the business of providing Unified Access Services from 1st April 2020 to 31 March 2021 at cost of Rs. 5Cr."
Redacted sentence: "ORG1 is engaged in the business of providing Unified Access Services from XXXXX to XXXXX at cost of Rs. XXXXX."

## What file formats are supported?
Currently, PDF, DOC and DOCX files are supported. All the files are converted to DOCX files before processing.
PDF files can be either scanned or digitally readable. It is recommended to have digitally readable PDFs. For scanned PDF files, the table structures are lost and hence the output might not be as expected. For digitally readable PDF files, the table structures are retained.

## What languages are supported?
Currently only English language is supported.

# 🔧 2. Installation
## 2.1 Recommended Hardware
It is required to use a machine with at least 6GB RAM and 4 cores. Having more RAM and cores will help in faster processing of the documents. 
## 2.1 Windows Installation
- Check if virtualization is enabled. [help](https://youtu.be/X2fKuPS3yIM) 
- If not, enable it from BIOS. [help1](https://support.microsoft.com/en-us/windows/enable-virtualization-on-windows-11-pcs-c5578302-6e43-4b4b-a449-8ced115f58e1), [help2](https://www.simplilearn.com/enable-virtualization-windows-10-article)
- Install WSL. Run following command in Command Prompt as Administrator:
```bash
wsl --install
```
- Change the resouce allocation for WSL to 4GB RAM and 2 cores. Feel free to add more resources if you have them. Run following command in Command Prompt as Administrator: 
```bash
type > %UserProfile%/.wslconfig
```
Open this file and put following contents in the file:
```
[wsl2]
memory=4GB
processors=4
```

- Install [podman](https://podman.io/)
- start podman service.
- Pull the docker image (7.5GB). Open Command Prompt as Administrator and run the following command:
```bash
podman pull docker.io/opennyaiofficial/legal_docs_redaction:latest_intel
```

## 2.2 Mac & Linux Installation
- Install [colima](https://github.com/abiosoft/colima) using Homebrew. ```brew install colima```
- Run the following command:
```bash
colima start --cpu 4 --memory 6G
```
- If you have Mac with M1 chip then ,Open Terminal and run the following command:
```bash
docker pull opennyaiofficial/legal_docs_redaction:latest_mac
```
- Else if you have Mac with Intel chip then ,Open Terminal and run the following command: 
```bash
docker pull opennyaiofficial/legal_docs_redaction:latest_intel
```

# 👩‍💻 3. Usage
Put all the files to be redacted in a folder. Create an empty folder where all the redacted files will be put.
Run the following command in Command Prompt or Terminal. Replace the input and output paths with the actual paths.
## 3.1 Windows or Linux or Intel Mac Usage
```bash
 podman run -v <input_folder_path>:/data/input -v <output_folder_path>:/data/output --rm opennyaiofficial/legal_docs_redaction:latest_intel
 ```

## 3.1 Mac with M1 chip Usage
```bash
docker run -v <input_folder_path>:/data/input -v <output_folder_path>:/data/output --rm opennyaiofficial/legal_docs_redaction:latest_mac
```