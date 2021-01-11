'''
from app.util.validate_files import allowed_file

#Test for check file type is valid or not
class TestClassFilename:

    #test case for test all file format
    def test_filenames(self):
        filenames = ["testing.pdf","texting.txt","testing.png","testing.jpg","testing.jpeg","testing.gif","testing.docx","testing.doc"]
        for filename in  filenames:
            file = allowed_file(filename=filename)
            assert file != None
            assert file == True

    #test case for test if filename cancatinate with two file extention
    def test_filename_extension(self):
        filename1 = "testing.txt.pdf"
        file = allowed_file(filename=filename1)
        assert file != None
        assert file == True
'''