import time
import datetime
import pandas as pd
import argparse
import logging
import torch
from torch.utils.data import Dataset, DataLoader

from metrics import calculate_accuracy, calculate_latency, calculate_topk
from agents.selenium_agent import GPTScriptAgent, MemoryGPTScriptAgent, RecommendAgent, SimpleScriptAgent, FastAgent
from utils.tools import close_driver


class QueryDataset(Dataset):
    def __init__(self, xlsx_file, start_pos):
        self.start_pos = start_pos
        self.df = pd.read_excel(xlsx_file)
        self.query = self.df['Query'][self.start_pos:1]
        self.url = self.df['Link'][self.start_pos:1]
        # self.script = self.df['Script'][start_pos:]
        
    def __len__(self):
        return len(self.query)
    
    def __getitem__(self, idx):
        query = self.query[idx+self.start_pos]
        url = self.url[idx+self.start_pos]
        # script = self.script[idx]
        return query, url

def evaluate_dataset(model_name, temperature, seed, memory, fast, vectorstore_type, start_pos, use_chromedriver):
    logger = logging.getLogger('AgentLogger')
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    now = datetime.datetime.now()

    if fast:
        file_handler = logging.FileHandler(f'logs/fast_{vectorstore_type}_{now}.log')
    else:
        file_handler = logging.FileHandler(f'logs/train_{model_name}_temp_{temperature}_{vectorstore_type}_{now}.log')

    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(log_formatter)
    file_handler.setFormatter(log_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    result_dict_list = []

    torch.manual_seed(seed)

    logger.info("BUILDING DATALOADER.")
    dataset = QueryDataset('data/kapwing_dataset.xlsx', start_pos=start_pos)
    train_loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    
    logger.info("INITIALIZING AGENT.")
    if memory:
        rec_agent = RecommendAgent(vectorstore_type=vectorstore_type)
        agent = MemoryGPTScriptAgent(model_name=model_name, 
                                     temperature=temperature,
                                     vectorstore_type="faiss",
                                     use_chromedriver=use_chromedriver
                                    )
    else:
        if fast:
            agent = FastAgent(model_name=model_name, 
                                temperature=temperature,
                                vectorstore_type=vectorstore_type,
                                use_chromedriver=use_chromedriver
                            )
        else:
            rec_agent = RecommendAgent(vectorstore_type=vectorstore_type)
            agent = SimpleScriptAgent(model_name=model_name, 
                                      temperature=temperature,
                                      vectorstore_type="faiss",
                                      use_chromedriver=use_chromedriver
                                    )

    logger.info("STARTING EVALUATION.")
    for i, (query, url) in enumerate(train_loader):
        try:
            if fast:
                print(f"RUNNING QUERY - {query[0]}.")
                latency, done, top3, index, rec_list = agent.run(query[0], url[0])

                result_dict = {}
                result_dict["query"] = query[0]
                result_dict["time"] = latency
                result_dict["done"] = done
                result_dict["top@3"] = top3

                result_dict["url"] = url[0]
                result_dict["rec_list_1"] = rec_list[0]
                result_dict["rec_list_2"] = rec_list[1]
                result_dict["rec_list_3"] = rec_list[2]
                result_dict["rec_picked"] = index

                logger.info(f"TOP@3 IS - {top3}.")
            else:
                print(f"RUNNING QUERY - {query[0]}.")
                objective, rec_latency = rec_agent.run(query[0])
                logger.info(f"DONE RECOMMENDING {query[0]}.")
                logger.info(f"RUNNING TIME IS {rec_latency}.")

                start_time = time.time()
                latency, done = agent.run(query[0])
                end_time = time.time()
                latency = end_time - start_time
                # done = (script[0] == agent.get_executor_scripts())
            
                result_dict = {}
                result_dict["query"] = query[0]
                result_dict["time"] = latency
                result_dict["done"] = done
                result_dict["rec_time"] = rec_latency

            result_dict_list.append(result_dict)
            logger.info(f"DONE {query[0]}.")
            logger.info(f"RUNNING TIME IS {latency}.")
            logger.info(f"IS FININSH - {done}.")
            
        except Exception as e:
            print(f'RUNNING {query[0]} FAILED. ERROR REPORT IS {e}.')

            result_dict = {}    
            result_dict["query"] = query[0]
            result_dict["time"] = 0.0
            result_dict["done"] = False

            if not fast:
                result_dict["rec_time"] = 0.0
            else:
                result_dict["top@3"] = False

            result_dict_list.append(result_dict)
            logger.info(f"FAILED {query[0]}.")

            continue
    
    mean_acc = calculate_accuracy(result_dict_list)

    if fast:
        mean_latency = calculate_latency(result_dict_list)
        mean_top3 = calculate_topk(result_dict_list, k=3)
        logger.info(f"The mean accuracy is {mean_acc}.")
        logger.info(f"The mean latency is {mean_latency}.")
        logger.info(f"The mean top3 accuracy is {mean_top3}.")

        df = pd.DataFrame(result_dict_list)
        df.to_excel(f'logs/fast_{vectorstore_type}_{now}.xlsx', index=False)

        return mean_acc, mean_latency, 0, mean_top3
    else:
        mean_latency, mean_rec_latency = calculate_latency(result_dict_list)
        logger.info(f"The mean accuracy is {mean_acc}.")
        logger.info(f"The mean latency is {mean_latency}.")
        logger.info(f"The mean recommendation latency is {mean_rec_latency}.")
        return mean_acc, mean_latency, mean_rec_latency, 0


def test(args):
    acc, latency, rec_latency, mean_top3 = evaluate_dataset(model_name=args.model_name, 
                                                            temperature=args.temperature,
                                                            seed=args.seed,
                                                            memory=args.memory,
                                                            fast=args.fast,
                                                            vectorstore_type=args.vectorstore_type,
                                                            start_pos=args.start_pos,
                                                            use_chromedriver=args.use_chromedriver
                                                        )
    close_driver()
    print('FINISH.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluation of Kapwing Agent.')
    parser.add_argument('--model_name', type=str, default='gpt-4') # No need for Fast Agent
    parser.add_argument('--temperature', type=int, default=0) # No need for Fast Agent
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--memory', type=bool, default=False) # TODO: Please don't use this for testing
    parser.add_argument('--fast', type=bool, default=True)  # TODO: Please use fast 
    parser.add_argument('--vectorstore_type', type=str, default='gpt-index')
    parser.add_argument('--start_pos', type=int, default=0) # TODO: Use only shuffle=False
    parser.add_argument('--use_chromedriver', type=bool, default=True)
    args = parser.parse_args()

    test(args)
