import argparse
import sys

def main():
    if (len(sys.argv) > 1):
        parser = argparse.ArgumentParser(description="GraXpert,the astronomical background extraction tool")
        parser.add_argument("filename", type = str, help = "Path of the unprocessed image")
        parser.add_argument('-correction', '--correction', nargs='?', const = "Subtraction", type=str, help = "Subtraction or Division")
        
        args = parser.parse_args()
        
        from graxpert.CommandLineTool import CommandLineTool
        clt = CommandLineTool(args)
        clt.execute()
        
        
    else:
        import graxpert.gui
    
    
    
if __name__ == "__main__":
    main()