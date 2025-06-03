from pathlib import Path 
import pandas as pd

class SampleSheet() :
    """
    Given a path to a samplesheet, will generate a SampleSheet object containing the structured information in the sheet.
    """

    def _handle_field(self, header:str, data) :
        """Adds data to a class attribute depending on the samplesheet field (`[Header], [Settings], [Reads], [Data]`)"""
        header = header.lower()
        if header in ["header", "settings"] :
            data = {d[0]:d[1] for d in data}
        elif header == "reads" :
            data = [d[0] for d in data]
        elif header == "data" :
            data = pd.DataFrame(data[1:], columns=data[0])
            self.samples = data["Sample_Name"].to_list()
        else :
            # for now, because I don't know any other case
            raise Exception(f"Unexpected header : '{header}'")

        setattr(self, header, data)
    
    def __init__(self, f:Path) -> None:
        self.path = f
        self.header : dict = None
        self.reads : list = None
        self.settings : dict = None
        self.data : pd.DataFrame = None
        
        fields = {}
        
        with open(f) as fp :
            try :
                lines = fp.readlines()
            except UnicodeDecodeError as e :
                raise e.__init__(f"Some characters in the samplesheet {f} could not be decoded, raising the following error : \n{e.__str__()}")

            curr_header = ""
            
            for line in lines :
                line = line.strip()
                if line.startswith("[") : 
                    curr_header = line.strip("[],;")
                    fields[curr_header] = []
                elif line == "" :
                    pass
                else :
                    fields[curr_header].append(line.split(","))

        for header, data in fields.items() :
            self._handle_field(header, data)

    def to_fastq(self, prefix="") :

        if self.samples is None :
            raise Exception(f"No sample within samplesheet : {self}")

        fq_list=  []
        for read in ["R1", "R2"] :
            fq_list += [f"{s}_S{i+1}_{read}_001.fastq.gz" for i, s in enumerate(self.samples)]
        return [str(Path(prefix)/fq) for fq in fq_list]

    def __repr__(self) -> str:
        s = f"SampleSheet : {self.path}\n"
        s+= f"    [Reads] : {self.reads}\n"
        for header in  ["header", "settings"] :
            s += f"    - {header}\n"
            for k, v in getattr(self,header).items() :
                s += f"        - {k} : {v}\n"
        
        s += f"    - {len(self.samples)} samples : {self.samples}"
        return s