# VChain合约的几点说明
## method：
### init: 初始化合约
### create_account: 生成结点账户，初始余额为100元，并将账户余额保存到本地
### join: 向vchain_account转账3元作为保证金，并将账户余额保存到本地
### maintain: 向vchain_account转账1元维持在线的状态，并将账户余额保存到本地
### active_quit: 向vchain_account转账0元以表示自己想要退出VChain，将节点缴纳的押金退回并将账户余额保存到本地
## checker:
### create_account_checker: 验证create_account的正确性
### join_checker: 验证join的正确性
### maintain_checker: 验证join的正确性
### active_quit_checker: 验证active_quit的正确性
## 记录文件:
### pub_priv.txt: 记录用户生成的公私钥对
### balance.txt: 记录结点账户的余额
