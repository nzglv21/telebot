a = {'a':123, 'b':234}
import pickle
with open('a.pkl', 'wb') as f:
    pickle.dump(a, f)
        
with open('a.pkl', 'rb') as f:
    loaded_dict = pickle.load(f)

print(loaded_dict)