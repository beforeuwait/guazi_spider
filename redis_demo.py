import redis
import time
import json
pool = redis.StrictRedis(host='localhost', port=6379, db=1)

# pool.set('cookie_status', {'0': '1'})
# pool.delete('cookie_status')
# print(pool.get('hello'))
# print(pool.get('key1').decode())

# pool.lpush('cookie_status', '1_1')
# pool.lpush('cookie_status', '2_1')
# pool.lpush('cookie_status', '3_1')
# pool.lpush('cookie_status', '4_1')
# pool.lpush('cookie_status', '5_1')
# pool.lpush('first', 'jia')
# pool.lpush('first', 'wei')

# print(pool.rpop('first').decode())
#
# print(pool.exists('first'))

while True:
    if pool.exists('ssnrep'):
        a = pool.rpop('ssnrep')
        print(a)
    time.sleep(0.1)

# seed = {"brand_id": "1199", "brand": "奥迪", "serise_id": "29", "serise": "奥迪200", "p_type": "合资", "url": "https://www.guazi.com/zz/dealrecord?tag_id=29&date=2018100", "check_city": "zz", "date": "2018-1", "cookie": {}, "data": [], "cookie_status": 0, "epoh": 9}
#
# pool.lpush('ssnreq', json.dumps(seed))