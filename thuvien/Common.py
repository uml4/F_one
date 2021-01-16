import json


class Common:
    

    def write_file(self):        

        with open('command.json', 'w') as json_file:
            json.dump(command_dict, json_file)

    def write_init_file(self, command_dict):
        command_dict = {"name": "Bob",
                        "ra_lenh_canh_tay_gn" : 0
            }
        self.write_file(command_dict)


    def read_command_file(self):
        data = {}
        with open('command.json') as f:
            data = json.load(f)

        # Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
        print(data)
        return data

    def ghi_ra_lenh_canh_tay(self, value):
        data = self.read_command_file()
        data["ra_lenh_canh_tay_gn"] = value

        self.write_file(data)