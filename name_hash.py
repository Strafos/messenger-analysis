class NameHasher():
    def __init__(self):
        with open("name_dump.txt", "r") as f:
            self.anon_names = [name.strip() for name in f.readlines()]

    def hash_by_index(self, index):
        """Given an index, return a name"""
        bounded_index = index % len(self.anon_names)
        return self.anon_names[bounded_index]

    def hash_by_name(self, name_in):
        """Hash an input name to an anonymous name"""
        index = hash(name_in)
        return self.hash_by_index(index)