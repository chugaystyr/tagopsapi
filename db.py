import psycopg2
from datetime import datetime
import json


class DB:

	def __init__(self):
		self.conn = psycopg2.connect(
							host="localhost",
							database="tags",
							user="postgres",
							password="root")


	def inset(self, tagopsSecret, tagopsBucket, data):
		now = datetime.now().strftime("%Y-%m-%d")
		query = f"""INSERT INTO tags (created, jval, val, usersecret, userbucket) VALUES ('{now}', '{json.dumps(data['jval'])}', '{data['val']}', {tagopsSecret}, '{tagopsBucket}');"""
		cur = self.conn.cursor()
		cur.execute(query)
		id = cur.fetchone()[0]
		self.conn.commit()
		return True if id else False
	
	def get_tag(self, tag_id):
		query = f"""SELECT * from tags where id = {int(tag_id)} """
		cur = self.conn.cursor()
		cur.execute(query)
		res = cur.fetchone()
		return res
	
	def get_tag_list(self, limit=10):
		query = f"""SELECT * from tags limit {limit} """
		cur = self.conn.cursor()
		cur.execute(query)
		return cur.fetchall()
