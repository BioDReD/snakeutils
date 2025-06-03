from pathlib import Path 
import pandas as pd
from collections import Counter
import re

def check_sample_is_valid(name) : 
    accepted = r"[A-z0-9-\_]*"
    try : 
        matched = re.finditer(accepted, name).__next__()[0]
        return matched == name
    except Exception : 
        return False

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
            c = Counter(self.samples)
            potential_dup = {k for k, val in c.items() if val > 1}
            if potential_dup : 
                raise Exception(f"The following samples are duplicated ! {potential_dup}")

            errors = []
            for sample in self.samples : 
                if not check_sample_is_valid(sample):  
                    errors.append(sample)
            if errors : 
                sep = "\n-"
                raise Exception(f"The following samples have names with invalid characters. They must countain only alphanumeric characters and '-' or '_'. {sep}{sep.join(errors)}")

            data = "Not used"
        else :
            # for now, because I don't know any other case
            raise Exception(f"Unexpected header : '{header}'")

        setattr(self, header, data)
    
    def __init__(self, path:Path) -> None:
        path = Path(path)
        self.name = path.name
        self.header : dict = {}
        self.reads : list = None
        self.settings : dict = {}
        self.data : pd.DataFrame = None
        self.lines = path.read_text().split("\n")

        fields = {}
        curr_header = ""
        
        for line in self.lines :
            line = line.strip()
            if line.startswith("[") : 
                curr_header = line.strip("[],;")
                fields[curr_header] = []
            elif line == "" :
                pass
            else :
                data = [l for l in line.split(",") if l]
                if data :
                    fields[curr_header].append(data)

        for header, data in fields.items() :
            self._handle_field(header, data)

    def __repr__(self) -> str:
        s = f"SampleSheet : {self.name} \n"
        s+= f"    [Reads] : {self.reads}\n"
        for header in  ["header", "settings"] :
            s += f"    - {header}\n"
            for k, v in getattr(self,header, {}).items() :
                s += f"        - {k} : {v}\n"
        
        sep = "\n        - "
        s += f"    - {len(self.samples)} samples : {sep + sep.join(self.samples)}"
        return s
    
    def to_fastq(self, prefix="") :
        """Returns a list of paths corresponding to all expected fastqs. If a prefix is given, it is considered to be a folder that will be the destination of these fastqs."""
        if self.samples is None :
            raise Exception(f"No sample within samplesheet : {self}")

        fq_list=  []
        for read in ["R1", "R2"] :
            fq_list += [f"{s}_S{i+1}_{read}_001.fastq.gz" for i, s in enumerate(self.samples)]
        return [str(Path(prefix)/fq) for fq in fq_list]