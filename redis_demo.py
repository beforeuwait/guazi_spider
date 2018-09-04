import redis

pool = redis.StrictRedis(host='localhost', port=6379, db=0)

# pool.set('cookie_status', {'0': '1'})
# pool.delete('cookie_status')
# print(pool.get('hello'))
# print(pool.get('key1').decode())

pool.lpush('cookie_status', '1_1')
pool.lpush('cookie_status', '2_1')
pool.lpush('cookie_status', '3_1')
pool.lpush('cookie_status', '4_1')
pool.lpush('cookie_status', '5_1')
# pool.lpush('first', 'jia')
# pool.lpush('first', 'wei')

# print(pool.rpop('first').decode())
#
# print(pool.exists('first'))