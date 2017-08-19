with pab as (
		/*拼团表*/ 
		select 
		id promotion_id, 
		name topic_name, 
		date_parse(start_time,'%Y-%m-%d %H:%i:%S') start_time, 
		date_parse(end_time,'%Y-%m-%d %H:%i:%S') end_time 
		from ods.pr_activity_base 
		where name is not null and name not like '%test%' and name not like '%测试%'
		),
	 pai as (
			 /*拼团商品表*/ select 
			 activity_id promotion_id, 
			 avg(activity_price) activity_price 
			 from ods.pr_activity_item 
			 group by 1
			),
temp as (select 1)
	select
		pab.promotion_id,
		topic_name,
		activity_price,
		start_time,
		end_time,
		date_diff('day',start_time,end_time) last_time
	from
		pab
		join pai using(promotion_id)