# VChain合约的几点说明
## method：
### init: 初始化合约
### create_account: 生成结点账户，初始余额为100元
### join: 向vchain_account转账3元作为保证金
### maintain: 向vchain_account转账1元维持在线的状态
### active_quit: 向vchain_account转账0元以表示自己想要退出VChain
## checker:
### create_account_checker: 验证create_account的正确性，并将账户余额保存到本地
### join_checker: 验证join的正确性，并将账户余额保存到本地
### maintain_checker: 验证join的正确性，并将账户余额保存到本地
### active_quit_checker: 验证active的正确性， 将节点缴纳的押金退回并将账户余额保存到本地
## 记录文件:
### pub_priv.txt: 记录用户生成的公私钥对
### balance.txt: 记录结点账户的余额
