
#!/usr/bin/env python
# Implementation of collaborative filtering recommendation engine


# from recommendation_data import dataset
from math import sqrt

dataset = {}

def similarity_score(person1,person2):

	# Returns ratio Euclidean distance score of person1 and person2

	both_viewed = {}		# To get both rated items by person1 and person2

	for item in dataset[person1]:
		if item in dataset[person2]:
			both_viewed[item] = 1

		# Conditions to check they both have an common rating items
		if len(both_viewed) == 0:
			return 0

		# Finding Euclidean distance
		sum_of_eclidean_distance = []

		for item in dataset[person1]:
			if item in dataset[person2]:
				sum_of_eclidean_distance.append(pow(dataset[person1][item] - dataset[person2][item],2))
		sum_of_eclidean_distance = sum(sum_of_eclidean_distance)

		return 1/(1+sqrt(sum_of_eclidean_distance))

def pearson_correlation(person1,person2):

	# To get both rated items
	both_rated = {}
	for item in dataset[person1]:
		if item in dataset[person2]:
			both_rated[item] = 1

	number_of_ratings = len(both_rated)
	# print both_rated
	# Checking for number of ratings in common
	if number_of_ratings == 0:
		return 0

	# Add up all the preferences of each user
	person1_preferences_sum = sum([dataset[person1][item] for item in both_rated])
	person2_preferences_sum = sum([dataset[person2][item] for item in both_rated])

	# Sum up the squares of preferences of each user
	person1_square_preferences_sum = sum([pow(dataset[person1][item],2) for item in both_rated])
	person2_square_preferences_sum = sum([pow(dataset[person2][item],2) for item in both_rated])

	# Sum up the product value of both preferences for each item
	product_sum_of_both_users = sum([dataset[person1][item] * dataset[person2][item] for item in both_rated])

	# Calculate the pearson score
	numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)
	denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
	if denominator_value == 0:
		return 0
	else:
		r = numerator_value/denominator_value
		return r

def calculate_sim_pearson_score(person1, person2):
	# To get both rated items
	both_rated = {}
	# import pdb; pdb.set_trace()
	try:
		for item in dataset[person1]:
			if item in dataset[person2]:
				both_rated[item] = 1
	except KeyError:
		return 0

	# Number of ratings both person rated
	number_of_ratings = len(both_rated)

	number_of_ratings1 = len(dataset[person1])

	number_of_ratings2 = len(dataset[person2])

	# Checking for number of ratings in common
	if number_of_ratings == 0:
		return 0

	# print(type(both_rated))
	# print [dataset[person1][item] for item in both_rated]
	# print number_of_ratings
	rated_everage_person1 = sum([dataset[person1][item] for item in dataset[person1]]) / number_of_ratings1
	rated_everage_person2 = sum([dataset[person2][item] for item in dataset[person2]]) / number_of_ratings2
	# print rated_everage_person1, rated_everage_person2

	# tuso = [sum((dataset[person1][item] - rated_everage_person1) * (dataset[person2][item] - rated_everage_person2)) for item in both_rated]

	# mauso = [sum(pow((dataset[person1][item] - rated_everage_person1), 2)) * sum(pow((dataset[person2][item] - rated_everage_person2), 2)) for item in both_rated]

	tuso = sum([(dataset[person1][item] - rated_everage_person1) * (dataset[person2][item] - rated_everage_person2) for item in both_rated])
	mauso = sqrt(sum([pow((dataset[person1][item] - rated_everage_person1), 2) for item in both_rated]) * sum([pow((dataset[person2][item] - rated_everage_person2), 2) for item in both_rated]))
	# print tuso

	if mauso == 0:
		return 0
	else:
		return tuso / mauso

def most_similar_users(person, number_of_users):
	# returns the number_of_users (similar persons) for a given specific person.
	scores = [(pearson_correlation(person,other_person),other_person) for other_person in dataset if  other_person != person ]

	# Sort the similar persons so that highest scores person will appear at the first
	scores.sort()
	scores.reverse()
	return scores[0:number_of_users]

def k_nearest_users(person, number_of_users):
	# returns the number_of_users (similar persons) for a given specific person.
	scores = [(calculate_sim_pearson_score(person,other_person),other_person) for other_person in dataset if  other_person != person ]

	# Sort the similar persons so that highest scores person will appear at the first
	scores.sort()
	scores.reverse()
	return scores[0:number_of_users]

def user_recommendations(person, k_nearest = 4):

	# Gets recommendations for a person by using a weighted average of every other user's rankings
	totals = {}
	simSums = {}
	rankings_list =[]
	for other in dataset:
		# don't compare me to myself
		if other == person:
			continue
		sim = pearson_correlation(person,other)
		# ignore scores of zero or lower
		if sim <=0:
			continue
		for item in dataset[other]:
			if item not in dataset[person] or dataset[person][item] == 0:
			# Similrity * score
				totals.setdefault(item, 0)
				totals[item] += dataset[other][item] * sim
				# Sum of similarities
				simSums.setdefault(item, 0)
				simSums[item]+= sim

		# Create the normalized list

	rankings = [(total/simSums[item],item) for item,total in totals.items()]
	rankings.sort()
	rankings.reverse()
	# returns the recommended items
	recommendataions_list = [recommend_item for score,recommend_item in rankings]
	return rankings[:k_nearest]

def user_recommendations_pearson(person, k_nearest = 4):
	person = str(person)
	# Tim ra k nguoi dung co do tuong tu gan nhat voi person
	simlilar_users = k_nearest_users(person, k_nearest)

	# Tong so item da duoc nguoi dung danh gia
	if person in dataset:
		number_of_ratings = len(dataset[person])
	else:
		return []

	# Gia tri danh gia trung binh tren tat ca cac item cua nguoi dung
	rated_everage = sum([dataset[person][item] for item in dataset[person]]) / number_of_ratings

	#
	# tuso = sum([ for score, other in most_similar_users])
	totals = {}
	simSums = {}
	rankings_list =[]
	for score, other in simlilar_users:
		other = str(other)
		sim = calculate_sim_pearson_score(person, other)
		if sim <= 0:
			continue

		# Tong so item da duoc nguoi dung danh gia
		number_of_ratings_other = len(dataset[other])

		# Gia tri danh gia trung binh tren tat ca cac item cua nguoi dung
		rated_everage_other = sum([dataset[other][item] for item in dataset[other]]) / number_of_ratings_other

		for item in dataset[other]:
			try:
				# item = int(item)
				if item not in dataset[person] or dataset[person][item] == 0:
				# Similrity * score
					totals.setdefault(item, 0)
					totals[item] += sim * (dataset[other][item] - rated_everage_other)
					# Sum of similarities
					simSums.setdefault(item, 0)
					simSums[item] += abs(sim)
			except:
				pass

	rankings = [(rated_everage + total/simSums[item],item) for item,total in totals.items()]
	rankings.sort()
	rankings.reverse()
	# returns the recommended items
	recommendataions_list = [(score, recommend_item) for score,recommend_item in rankings]
	return recommendataions_list[:k_nearest]
