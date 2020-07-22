# PriorityQueue Klasse
# A simple implementation of Priority Queue 
# using Queue. 
class PriorityQueue(object): 
    def __init__(self,order=''): 
        self.order = order
        self.queue = [] 
  
    def __str__(self): 
        return ' '.join([str(i) for i in self.queue]) 

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_and_delete()

    # for checking if the queue is empty 
    def isEmpty(self): 
        return len(self.queue) == [] 
    
    def exist(self, item):
        if item in self.queue:
            return True
    
    def empty(self):
        self.queue = []
    
    # Get the Length of the queue
    def get_size(self):
        return len(self.queue)
  
    # for inserting an element in the queue 
    def insert(self, data): 
        if not self.exist(data):
            self.queue.append(data) 
  
    # for getting and popping an element based on lowest Cost 
    def get_and_delete(self): 
        try: 
            if len(self.queue) == 0:
                return False
            min = 0
            for i in range(len(self.queue)): 
                # print(self.queue[i].position)
                if self.order == 'finish':
                    if self.queue[i].get_estimated_cost_to_finish() < self.queue[min].get_estimated_cost_to_finish(): 
                        min = i 
                elif self.order == 'start':   
                    if self.queue[i].get_cost_from_start() < self.queue[min].get_cost_from_start(): 
                        min = i 
                else:
                    if self.queue[i].get_total_cost() <= self.queue[min].get_total_cost(): 
                        min = i 
            item = self.queue[min] 
            del self.queue[min] 
            return item 
        except IndexError: 
            print('IndexError')
            return False
            exit() 

    def delete_all(self):
        self.queue = []
    def get_tile_and_delete(self, tile):
        index = self.queue.index(tile)
        tile = self.queue[index]
        del self.queue[index]
        return tile

    
    def get_cost_from_start(self, tile):
        index = self.queue.index(tile)
        return self.queue[index].cost_from_start