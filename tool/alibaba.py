from http import HTTPStatus
import dashscope
import os
from config import Alibaba_config
from tool.pdf import get_pdf_text
from tool.zhipu import zero_shot_prompt

classification_prompt = """
任务：分析给定论文（标题和摘要）是否适用于智能驾驶领域，如适用则进行子领域分类（6个以内）。
角色：你是智能驾驶领域的专家，精通各个子领域的最新进展和技术应用。你能准确判断论文是否与智能驾驶相关，并能识别其主要贡献所属的具体子领域。
背景：智能驾驶是一个快速发展的跨学科领域，涉及计算机视觉、传感器融合、路径规划、决策控制等多个方面。近年来，深度学习和人工智能技术在该领域的应用日益广泛，带来了许多创新性的解决方案。
输出格式：
1. 应用判断：[Y/N]
2. 子领域分类：[子领域名称]（如应用判断为"Y"）
3. 分类理由：[简要说明论文与该子领域的关联及对智能驾驶的潜在贡献] （如应用判断为"Y"）

注意事项：
- 一定要保证格式完整，保留中括号！保留中括号！保留中括号！否则无法识别！！！
- 分析核心内容和创新点，选择最主要的子领域。
- 考虑技术或方法的应用潜力，保持客观严谨。
- 最多给出3行内容。
- 如输入与论文无关，按非智能驾驶相关提示回答，保持3行。
- 不用太直接关联，稍微有些关联也可以分类

子领域如下（限定以下领域，每一行都是一个完整的子领域（忽略后面括号的内容），请不要拆分，不要分类到其他领域！）：

道路场景理解与分析（包括车道线检测、交通标志识别、路况分析等）
车辆与行人检测跟踪（包括实时目标检测、多目标跟踪、姿态估计，图像增强等）
视觉导航与运动规划（包括视觉里程计、视觉SLAM、基于视觉的路径规划等）
定位、建图与路径规划
行为预测与决策控制
仿真与数据生成（包括虚拟环境构建、合成数据生成等）

请严格按照输出格式进行输出！（方括号内容可变，其他格式不变，包括保留方括号!!!）
- 一定要保证格式完整，保留中括号！保留中括号！保留中括号！否则无法识别！！！
- 一定要保证格式完整，保留中括号！保留中括号！保留中括号！否则无法识别！！！
"""


def get_classification_result_by_tongyi(content):
    if content is None or content == "":
        return []
    messages = [
        {"role": "system", "content": classification_prompt},
        {"role": "user", "content": content},
    ]

    response = dashscope.Generation.call(
        model="qwen-max",
        api_key=Alibaba_config.API_KEY,
        messages=messages,
        result_format="text"
    )
    if response.status_code == HTTPStatus.OK:
        return response.output.text.split("\n")
    else:
        return []


def get_result_by_tongyi(system_prompt, content):
    if content is None or content == "":
        return []
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]

    response = dashscope.Generation.call(
        model="qwen-max-longcontext",
        api_key=Alibaba_config.API_KEY,
        messages=messages,
        result_format="message",
        stream=True,
        incremental_output=True
    )
    for chunk in response:
        if chunk.status_code == HTTPStatus.OK:
            print(chunk.output.choices[0]['message']['content'], end='')
            yield chunk.output.choices[0]['message']['content']
        else:
            print("error")


if __name__ == '__main__':
    text = get_pdf_text("../data/pdfs/Song_Collaborative_Semantic_Occupancy_Prediction_with_Hybrid"
                        "_Feature_Fusion_in_Connected_CVPR_2024_paper.pdf")
    test = """
    title:Attribute-Guided Pedestrian Retrieval: Bridging Person Re-ID with Internal Attribute Variability
    abstract:In various domains such as surveillance and smart retail, pedestrian retrieval, centering on person re-identiﬁcation (Re-ID), plays a pivotal role. Existing Re-ID methodologies often overlook subtle internal attribute variations, which are crucial for accurately identifying individuals with changing appearances. In response, our paper introduces the Attribute-Guided Pedestrian Retrieval (AGPR) task, focusing on integrating speciﬁed attributes with query images to reﬁne retrieval results. Although there has been progress in attribute-driven image retrieval, there remains a notable gap in effectively blending robust Re-ID models with intra-class attribute variations. To bridge this gap, we present the Attribute-Guided Transformer-based Pedestrian Retrieval (ATPR) framework. ATPR adeptly merges global ID recognition with local attribute learning, ensuring a cohesive linkage between the two. Furthermore, to effectively handle the complexity of attribute interconnectivity, ATPR organizes attributes into distinct groups and applies both inter-group correlation and intra-group decorrelation regularizations. Our extensive experiments on a newly established benchmark using the RAP dataset [32] demonstrate the effectiveness of ATPR within the AGPR paradigm.
    """
    print(get_result_by_tongyi(zero_shot_prompt, text))
    # get_result_by_tongyi(classification_prompt, test)
