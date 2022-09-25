from datetime import date
import json

class googlechat_trainer:
    def __init__(self, path):
        # requires text files instead of json since raw chat data is in a weird form
        self.raw_data = open(path, 'r', encoding="utf8").read()
        self.raw_data = self.raw_data.split('\n\n')

    def format_data(self, output_path):
        self.parsed_data = []
        for entry in self.raw_data:
            for i in range(1, len(entry.split('\n'))):
                # time is saved in %H:%S since Gchat auto formatted times
                try:
                    # convert to 24 hour format
                    unf = entry.split('\n')[0].split(',')[2][1:].replace(' AM', '')
                    if 'PM' in unf:
                        if int(unf.split(":")[0]) + 12 >= 24:
                            formatted_time = f'{int(unf.split(":")[0]) + 11}:{unf.split(":")[1].replace(" PM", "")}'
                        else:
                            formatted_time = f'{int(unf.split(":")[0]) + 12}:{unf.split(":")[1].replace(" PM", "")}'
                    else:
                        formatted_time = unf

                    self.parsed_data.append({
                        'content': entry.split('\n')[i],
                        'author': entry.split('\n')[0].split(',')[0],
                        'time': formatted_time
                    })
                except IndexError:
                    try:
                        for j, char in enumerate(entry.split('\n')[0].split(',')[1]):
                            if char in list('123456789'): break

                        # convert to 24 hour format
                        unf = entry.split('\n')[0].split(',')[1][j:].replace(' AM', '')
                        if 'PM' in unf:
                            if int(unf.split(":")[0])+12 >= 24:
                                formatted_time = f'{int(unf.split(":")[0])+11}:{unf.split(":")[1].replace(" PM", "")}'
                            else:
                                formatted_time = f'{int(unf.split(":")[0])+12}:{unf.split(":")[1].replace(" PM", "")}'
                        else:
                            formatted_time = unf

                        self.parsed_data.append({
                            'content': entry.split('\n')[i],
                            'author': entry.split('\n')[0].split(',')[0],
                            'time': formatted_time
                        })
                    except IndexError: pass

        data = []

        # use today as default since date differences don't really matter
        today = date.today().strftime("%Y-%m-%d")
        for item in self.parsed_data:
            data.append({
                'content': item['content'],
                'author': item['author'],
                'timestamp': f'{today}T{item["time"]}:00'
            })
        with open(output_path, 'w') as file:
            file.write(json.dumps(data, indent=4))
        return self.parsed_data
