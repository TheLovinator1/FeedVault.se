from reader import Reader, make_reader

reader: Reader = make_reader(url="testboi.sqlite")
reader.add_feed("http://485i.com/feed/")
reader.update_feeds()
