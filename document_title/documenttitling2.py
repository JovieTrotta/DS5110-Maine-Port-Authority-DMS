# -*- coding: utf-8 -*-

#Chris Kinley
#11/16


# main function that generates the title dictionary then renames all the documents (currently does not rename the pdf)
def main(path, pdf_path=""):
  from nltk.stem.snowball import SnowballStemmer
  import re
  import os
  from docx import Document

  # Obtain text from a Docx file. Returns a list of the words in the file
  def getText(filename):
    try:
      doc = Document(filename)
      raw = "\n".join(p.text for p in doc.paragraphs)
      text=raw.split()
      return text
    except Exception as e:
      return []

  # Finds month names in the a tokenized document and finds the year associated with it. Returns a dictionary of each month/year combo that appears and which spots in the list it appears in
  def find_dates(list):
    return_dict = {}
    months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    for i in range(len(list)):
      for month in months:
        if month in list[i].lower():
          for j in range(max(i-4,0),i+5):
            try:
              year = int(list[j])
            except:
              continue
            if year>1900 and year<2100:
              date = month + " " + str(year)
              if date not in return_dict:
                return_dict[date] = [i]
              else:
                return_dict[date].append(i)


    return_dict = {k: v for k, v in sorted(return_dict.items(), key=lambda item: item[1], reverse=True)}
    return return_dict


  #Tries to find a title "seed" based on the frequency dictionary and bifrequency dictionary.
  #Then grabs the first instance of this seed word and generates a title based on the surrounding words in the document
  def generate_name(text_entered, freq_dict_entered, bifreq_dict_entered):

    # Obtains a seed and uses not found as a return if no good seed is found
    freq_dict_hits = list(freq_dict_entered.keys())[0:5]
    bifreq_dict_hits = list(bifreq_dict_entered.keys())[0:5]
    for words in bifreq_dict_hits:
      if bifreq_dict_entered[words]<2:
        bifreq_dict_hits.remove(words)
    title_seed=""
    for hits in freq_dict_hits:
      for bi_hits in bifreq_dict_hits:
        if hits in bi_hits:
          if title_seed == "":
            title_seed = hits
    if title_seed == "":
      return "not found"

    # Generates a title based on the words that occur a little before and a little after the seed word
    list_splice = []
    for i in range(len(text_entered)):
      reduced_word = regex.sub('',text_entered[i].lower())
      if title_seed in reduced_word:
        list_splice = text_entered[max(0,i-2):i+12]
        list_splice = [regex_no_num.sub('',k.lower()) for k in list_splice]
        break
    title =  ""
    for i in list_splice:
      if i not in stopwords:
        title = title + i + " "

    # adds the date to the title if one can be found
    date_list = list(find_dates(text_entered).keys())
    if(len(date_list)>0):
      title = title + list(find_dates(text_entered).keys())[0]
    title = title.title()
    return title

  # Generates a frequency dictionary and a bifrequency dictionary from an input list that represents the tokenized document.
  #Returns two dictionaries with the word/phrases and how many times they occur in the first 250 decipherable words in the document
  def gen_freq_dicts(text_whole):

    # Cleans up the text. Also gets rid of empty words and words that are too long to try to filter out when the ocr did a poor job
    text = [regex_no_num.sub('',words.lower()) for words in text_whole if (len(regex_no_num.sub('',words.lower()))>0 and len(regex_no_num.sub('',words.lower()))<14)]
    text = text[0:min(len(text),250)]

    # create 1 word frequency dictionary
    freq_dict ={}
    for word in text:
      if word not in stopwords and len(word)>2 and len(word)<14:
        if word in freq_dict:
          freq_dict[word]= freq_dict[word]+1
        else:
          freq_dict[word] = 1

    #creating two word frequency dictionary
    bifreq_dict = {}
    old_word=""
    two_word=""
    for word in text:
      if word not in stopwords and len(word)>2 and len(word)<14:
        two_word = old_word + " " + word
        if two_word in bifreq_dict:
          bifreq_dict[two_word]= bifreq_dict[two_word]+1
        else:
          bifreq_dict[two_word] = 1
        old_word = word

    # sorts all the frequency dictionaries by frequencies
    freq_dict = {k: v for k, v in sorted(freq_dict.items(), key=lambda item: item[1], reverse=True)}
    bifreq_dict = {k: v for k, v in sorted(bifreq_dict.items(), key=lambda item: item[1], reverse=True)}


    return text,freq_dict, bifreq_dict


  # takes a folder path of .txt and .docx files and generates a dictionary of old titles of files and potential new titles for the files
  def generate_title_dictionary(folder_path):

    title_dictionary = {}

    # Deals with files being either docx or txt to get one list of words in the document
    directory = os.fsencode(folder_path)
    for file in os.listdir(directory):
      filename = os.fsdecode(file)
      if filename.endswith(".docx"):
        text_long=getText(folder_path + "/" + filename)
      elif filename.endswith(".txt"):
        with open(folder_path + "/" + filename, "r") as file_text:
          text_long=file_text.read().split()
      else:
        continue

      # Generates frequency dictionaries and then uses the generate name method to get a new potential name
      text_short, freq, bifreq = gen_freq_dicts(text_long)
      new_name = generate_name(text_short, freq, bifreq)

      # Deals with no good name found, will use original file name
      if new_name == "not found":
        title_dictionary[filename] = filename
      else:
        title_dictionary[filename] = new_name
    return title_dictionary

  # Finishes generating the whole file path and renames the files
  def rename_files(title_dictionary, file_path, pdf_file_path):

    # Creates a dictionary of pdf files and their new potential name (will be what it already is to begin with)
    pdf_dict = {}
    if pdf_file_path != "":
      directory = os.fsencode(pdf_file_path)
      for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".pdf"):
          filename = filename[:-4]
          pdf_dict[filename] = filename

    for original_titles in title_dictionary.keys():
      original_path = file_path + "/" + original_titles

      print(original_path)
      # If the file is a txt, will maintain the file being a txt with the renaming
      if original_path.endswith(".txt"):
        if title_dictionary[original_titles].endswith(".txt"):
          if original_titles[:-4] in pdf_dict:
            pdf_dict[original_titles[:-4]] = title_dictionary[original_titles][:-4]
          new_path = file_path + "/" + title_dictionary[original_titles]
        else:
          if original_titles[:-4] in pdf_dict:
            pdf_dict[original_titles[:-4]] = title_dictionary[original_titles]
          new_path = file_path + "/" + title_dictionary[original_titles].strip() + ".txt"




      # if the file is a docx, will maintain that scheme with the renaming
      elif original_path.endswith(".docx"):
        if title_dictionary[original_titles].endswith(".docx"):
          new_path = file_path + "/" + title_dictionary[original_titles]
        else:
          new_path = file_path + "/" + title_dictionary[original_titles].strip() + ".docx"


      #print(original_path)
      #print(new_path)
      os.rename(original_path, new_path)

    for pdf_titles in pdf_dict.keys():
      if pdf_dict[pdf_titles] != pdf_titles:
        os.rename(pdf_file_path + "/" + pdf_titles + ".pdf",pdf_file_path + "/" + pdf_dict[pdf_titles].strip() + ".pdf")


  regex = re.compile('[^a-zA-Z0-9]')
  regex_no_num = re.compile('[^a-zA-Z]')
  #stopwords list
  stopwords = ['', "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "shall", "page", "---"]


  dictionary =generate_title_dictionary(path)
  rename_files(dictionary, path, pdf_path)


if __name__=="__main__":
  main("/content/data","/content/pdfdata" )

