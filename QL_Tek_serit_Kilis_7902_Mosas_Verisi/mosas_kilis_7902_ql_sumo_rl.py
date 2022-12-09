""" REWARD (ÖDÜL): ÖNCEKİ ZAMAN ADIMINA GÖRE TOPLAM GECİKMENİN NE KADAR DEĞİŞTİĞİDİR. 

sumo-rl içinde traffic_signal.py de compute_reward fonksiyonu değiştirilerek farklı ödül 
fonksiyonları yazılabilir. BU python dosyasında hazır yazılmş henüz kullanılmayan reward 
fonksiyonlarıda mevcuttur.

"""
import argparse
import os
import sys
from datetime import datetime
from pytictoc import TicToc
#zaman değişkeni oluştur
t=TicToc()
t.tic() # zamanı başlat.
 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

import traci
from sumo_rl import SumoEnvironment
from sumo_rl.agents import QLAgent
from sumo_rl.exploration import EpsilonGreedy

if __name__ == '__main__':

    prs = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                  description="""Q-Learning Single-Intersection""")
    prs.add_argument("-route", dest="route", type=str, default='mosas_kilis_7902_static.net.xml', help="Route definition xml file.\n")
    prs.add_argument("-a", dest="alpha", type=float, default=0.1, required=False, help="Alpha learning rate.\n")
#GAMMA: öğrenmede bir önceki adımın bir sonraki adıma ne kadar etkisinin olacağı çok küçük verirsek 
#öğrenme hızında yavaşlama gerçekleşir.
    prs.add_argument("-g", dest="gamma", type=float, default=0.99, required=False, help="Gamma discount rate.\n")
    prs.add_argument("-e", dest="epsilon", type=float, default=0.05, required=False, help="Epsilon.\n")
    prs.add_argument("-me", dest="min_epsilon", type=float, default=0.005, required=False, help="Minimum epsilon.\n")
    prs.add_argument("-d", dest="decay", type=float, default=1.0, required=False, help="Epsilon decay.\n")
    prs.add_argument("-mingreen", dest="min_green", type=int, default=10, required=False, help="Minimum green time.\n")
    prs.add_argument("-maxgreen", dest="max_green", type=int, default=30, required=False, help="Maximum green time.\n")
    prs.add_argument("-gui", action="store_true", default=False, help="Run with visualization on SUMO.\n")
    prs.add_argument("-fixed", action="store_true", default=False, help="Run with fixed timing traffic signals.\n")# Sabit zamanlamalı trafik sinyalleriyle çalıştırma
    prs.add_argument("-s", dest="seconds", type=int, default=60000, required=False, help="Number of simulation seconds.\n")
    prs.add_argument("-r", dest="reward", type=str, default='wait', required=False, help="Reward function: [-r queue] for average queue reward or [-r wait] for waiting time reward.\n")
    prs.add_argument("-runs", dest="runs", type=int, default=1, help="Number of runs.\n")
    args = prs.parse_args()
    experiment_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") # çıktı csv dosyamızın adı
    out_csv = "{}_alpha{}_gamma{}_eps{}_decay{}".format(experiment_time, args.alpha, args.gamma, args.epsilon, args.decay)

    env = SumoEnvironment(net_file='mosas_kilis_static.net.xml',
                          route_file=args.route,
                          out_csv_name=out_csv,
                          use_gui=args.gui,
                          num_seconds=args.seconds,
                          min_green=args.min_green,
                          max_green=args.max_green,
                          sumo_warnings=False)

# Her run döngüsünde yeniden bir ortam oluşturulur. 
# Kendimize farklı en iyi olan arama uzayını oluşturmaya çalışıyoruz.
    for run in range(1, args.runs+1):
        initial_states = env.reset() # env.reset: Ortamı sıfırlar ve rastgele bir başlangıç ​​durumu döndürür.
         # Başlangıç değerleri ajana veriliyor.
        ql_agents = {ts: QLAgent(starting_state=env.encode(initial_states[ts], ts),
                                 state_space=env.observation_space,
                                 action_space=env.action_space,
                                 alpha=args.alpha,
                                 gamma=args.gamma,
                                 exploration_strategy=EpsilonGreedy(initial_epsilon=args.epsilon, min_epsilon=args.min_epsilon, decay=args.decay)) for ts in env.ts_ids}

        done = {'__all__': False}
        infos = []
        if args.fixed: # Sabit zamanlamalı trafik sinyalleriyle çalıştirma
            while not done['__all__']:
                _, _, done, _ = env.step({})
        else: # q learning ile calistirma
            while not done['__all__']:
                # EpsilonGreedy e gore action seciliyor
                actions = {ts: ql_agents[ts].act() for ts in ql_agents.keys()}
                # q_table, state, action_space ; değerlerine gore action seciliyor

                s, r, done, _ = env.step(action=actions)
                # done simülasyon step zamanı dolunca True dönüyor ve done bilgisi TRUE dönünce tamamlanıyor.

                for agent_id in ql_agents.keys():
                    # q learning formulu (bellman) uygulaniyor.
                    ql_agents[agent_id].learn(next_state=env.encode(s[agent_id], agent_id), reward=r[agent_id])
        
        env.save_csv(out_csv, run)
        env.close()
        t.toc() # Zamanı durdur ve hesapla.




