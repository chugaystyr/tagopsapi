import psycopg2
from datetime import datetime
import json
import os


class DB:

	def __init__(self):
		self.conn = psycopg2.connect(
							host=os.getenv('PG_HOST', 'localhost'),
							database=os.getenv('PG_DATABASE', 'tags'),
							user=os.getenv('PG_USER', 'postgres'),
							password=os.getenv('PG_PASSWORD', 'root'))

		self.buked_id = None


	def inset(self, tagopsSecret, tagopsBucket, data):
		now = datetime.now().strftime("%Y-%m-%d")
		query = f"""INSERT INTO tags (created, jval, val, usersecret, userbucket) VALUES ('{now}', '{json.dumps(data['jval'])}', '{data['val']}', {tagopsSecret}, '{tagopsBucket}') RETURNING id;"""
		cur = self.conn.cursor()
		try:
			cur.execute(query)
			id = cur.fetchone()
			self.conn.commit()
			return id
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
