#Generate desired citation style and save to CSV file for future retrieval.

import csv
import os

file_path = os.path.abspath("../../Bibliographies/mastersources.csv")

def get_source_information(csv_file):
  with open(csv_file, "r") as f:
    reader = csv.reader(f)
    source_information = []
    for row in reader:
      source_information.append(row)
  return source_information

def generate_citation(source_information, style):
  if style == "MLA":
    return generate_mla_citation(source_information)
  elif style == "APA":
    return generate_apa_citation(source_information)
  elif style == "Chicago":
    return generate_chicago_citation(source_information)
  elif style == "Harvard":
    return generate_harvard_citation(source_information)

def generate_mla_citation(source_information):
  author = source_information[0]
  title = source_information[1]
  publication_date = source_information[2]
  publisher = source_information[3]
  location = source_information[4]

  citation = f"{author}. {title}. {publication_date}. {publisher}, {location}."
  return citation

def generate_apa_citation(source_information):
  author = source_information[0]
  title = source_information[1]
  publication_date = source_information[2]
  publisher = source_information[3]
  location = source_information[4]

  citation = f"{author} ({publication_date}). {title}. {publisher}, {location}."
  return citation

def generate_chicago_citation(source_information):
  author = source_information[0]
  title = source_information[1]
  publication_date = source_information[2]
  publisher = source_information[3]
  location = source_information[4]

  citation = f"{author}. {title}. {publication_date}. {publisher}, {location}."
  return citation

def generate_harvard_citation(source_information):
  author = source_information[0]
  title = source_information[1]
  publication_date = source_information[2]
  publisher = source_information[3]
  location = source_information[4]

  citation = f"{author} ({publication_date}). {title}. {publisher}, {location}."
  return citation

def get_source_information():
    source_information = []
    author = input("Enter the author's name: ")
    title = input("Enter the title of the source: ")
    publication_date = input("Enter the publication date: ")
    publisher = input("Enter the publisher's name: ")
    location = input("Enter the location: ")

    source_information.append(author)
    source_information.append(title)
    source_information.append(publication_date)
    source_information.append(publisher)
    source_information.append(location)

    return source_information


def main():
    style = input("Which citation style do you want to use? (MLA, APA, Chicago, or Harvard): ")
    source_information = get_source_information()
    citation = generate_citation(source_information, style)
    column_names = ["Author", "Title", "Publication Date", "Publisher", "Location"]
    print(citation)

    # Append the citation to the CSV file
    with open(file_path, "a", newline="") as file:
        writer = csv.writer(file)
        if os.path.getsize(file_path) == 0:
            writer.writerow(column_names)
        writer.writerow(source_information + [citation])

if __name__ == "__main__":
    main()
