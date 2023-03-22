from datetime import datetime 
import textwrap as tr

class Log: 

    ## TO DO:
    ## add doc for all methods
    ## linebreaking in text wrap is not working properly. 

    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
    def header(self, message):
        cstr = ' message on ' + self.datetime + ' '
        print(cstr.center(100,'-'))
        print("{:^100}".format(message))
        #print("\r\n")
        #print('-'*100 + '\n')

    def create_file(self):
        f = open(self.path + "/" + self.filename, "w")
        f.close()
        cstr = ' started log on ' + self.datetime + ' '
        f = open(self.path + "/" + self.filename, "a")
        f.write(cstr.center(101,'-') + '\n' + '\n')
        f.close()

    def append_file(self, content):
        f = open(self.path + "/" + self.filename, "a")
        f.write(tr.fill(content, width = 98, replace_whitespace=False, 
                break_long_words=True) + '\n')
        f.close()

    def append_file_newline(self, content):
        f = open(self.path + "/" + self.filename, "a")
        f.write('\n' + tr.fill(content, width = 98, replace_whitespace=False, 
                break_long_words=True) + '\n'+ '\n')
        f.close()

        
    def add_log_line(self, message):
        f = open(self.path + "/" + self.filename, "a")
        cstr = ' added geoprocessing message on ' + self.datetime + ' '
        f.write('\n' + cstr.center(96,'-') + '\n' + 
                tr.fill(message, width = 98, replace_whitespace=False, 
                break_long_words=True) + '\n' + '-'*105 + '\n' + '\n')
        print("{:^100}".format(message))



