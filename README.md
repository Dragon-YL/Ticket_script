# Ticket_script
12306抢票脚本
改动自本视频：【12306抢票脚本傻瓜式教程python】https://www.bilibili.com/video/BV1uASRYPEHd?vd_source=36dc070c68e8e83e2f9edadc3b62dfe6
优化如下：
1.加快购票流程：
  使用WebDriverWait替代固定time.sleep
  优化元素查找和点击逻辑
  减少不必要的等待时间
  使用更快的轮询方式查找车票
2.登录优化：
  使用cookie保存登录状态
  自动检测cookie是否存在
  仅在必要时要求重新登录
3.定时功能优化：
  使用更精确的时间比较
  到时间直接抢票
