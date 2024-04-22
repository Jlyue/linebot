from collections import Counter
import numpy as np
import gym

# extract items from text
def extract_items_from_text(transcriptions, item_table):
    all_items = []
    for text in transcriptions:
        for item in item_table:
            if item.lower() in text.lower():
                all_items.append(item)
    return all_items

# generate score sheet
def generate_rating_table(all_items):
    item_counts = Counter(all_items)
    total_count = sum(item_counts.values())
    rating_table = {item: count / total_count for item, count in item_counts.items()}
    return rating_table

# reinforcement learning env
class RecommendationEnv(gym.Env):
    def __init__(self, rating_table):
        self.rating_table = rating_table
        self.items = list(rating_table.keys())
        self.action_space = gym.spaces.Discrete(len(self.items))
        self.observation_space = gym.spaces.Box(low=0, high=1, shape=(len(self.items),), dtype=np.float32)
        self.reset()

    def reset(self):
        self.user_preferences = np.zeros(len(self.items))
        return self.user_preferences

    def step(self, action):
        recommended_item = self.items[action]
        reward = self.rating_table[recommended_item]
        self.user_preferences[action] = reward
        done = True
        return self.user_preferences, reward, done, {}
