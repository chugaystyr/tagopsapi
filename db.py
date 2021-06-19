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

		self.buked_id = None


	def inset(self, tagopsSecret, tagopsBucket, data):
		now = datetime.now().strftime("%Y-%m-%d")
		query = f"""INSERT INTO tags (created, jval, val, usersecret, userbucket) VALUES ('{now}', '{json.dumps(data['jval'])}', '{data['val']}', {tagopsSecret}, '{tagopsBucket}');"""
		cur = self.conn.cursor()
		try:
			cur.execute(query)
			self.conn.commit()
			return True
		except Exception as e:
			print(str(e))
		return False

	def get_tag(self, tag_id):
		query = f"""SELECT * from tags where id = {int(tag_id)} and userbucket={self.buked_id}"""
		cur = self.conn.cursor()
		cur.execute(query)
		res = cur.fetchone()
		return res
	
	def get_tag_list(self, limit=10, offset=0):
		query = f"""SELECT * from tags WHERE userbucket={self.buked_id} OFFSET {offset} LIMIT {limit}"""
		cur = self.conn.cursor()
		cur.execute(query)
		return cur.fetchall()