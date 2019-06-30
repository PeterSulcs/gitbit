from gitbit.core import GitBit, generate_date_range
import datetime
import os
import json
from tqdm import tqdm


if __name__=="__main__":
    gb = GitBit()

    date_start = "2015-12-08"
    
    dates = list(generate_date_range(date_start))

    # Make data directories for heart data
    if not os.path.exists(os.path.join(".", "data")):
        os.mkdir(os.path.join(".", "data"))
    if not os.path.exists(os.path.join(".", "data", "hr")):
        os.mkdir(os.path.join(".", "data", "hr"))
    
    output_dir = os.path.join(".", "data", "hr")

    for d in tqdm(dates):
        data = gb.get_heart_rate_data(d)
        with open(os.path.join(output_dir, f"{d}.json"), "w") as fid:
            json.dump(data, fid)
