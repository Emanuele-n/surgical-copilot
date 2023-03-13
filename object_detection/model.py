"""
Implementation of YOLOv3 architecture
sources:
    https://arxiv.org/abs/1804.02767
    https://pjreddie.com/darknet/yolo/
    https://sannaperzon.medium.com/yolov3-implementation-with-training-setup-from-scratch-30ecb9751cb0
    https://www.youtube.com/watch?v=Grir6TZbc1M
"""

import torch
import torch.nn as nn

""" 
This is a code block defining the architecture configuration for the YOLOv3 (You Only Look Once version 3) object detection model. 
The YOLOv3 architecture is a convolutional neural network (CNN) that can detect objects in images and videos in real-time.
The configuration is stored in a list called config. Each item in the list represents a layer in the network, and is either a tuple or a string. 
The tuples represent convolutional layers and are structured as (filters, kernel_size, stride), where filters is the number of filters in the layer, kernel_size is the size of 
the convolutional kernel, and stride is the stride of the convolution. 
The strings indicate a specific type of layer, such as "B" for a residual block, "S" for a scale prediction block, and "U" for upsampling and concatenation with a previous layer.
The architecture is based on the Darknet-53 architecture, with additional layers added for detection at different scales. The final output of the network is a set of bounding boxes 
and associated object class probabilities for each object detected in the input image.

Filters Note: In a convolutional neural network (CNN), a filter is a small matrix of weights that is applied to the input data to produce a feature map. 
The size of the filter is usually square, and the number of elements in the filter is determined by the product of its height and width. 
The number of filters in a convolutional layer determines the number of output channels in the layer's output feature map.
For example, if a convolutional layer has 32 filters, it means that the layer will output a feature map with 32 channels. 
Each filter in the layer will be applied to the input data to produce one channel in the output feature map. 
Each filter learns to detect a different feature or pattern in the input data, and the output channels represent different combinations of these learned features.
Increasing the number of filters in a convolutional layer can increase the network's ability to capture complex patterns and features in the input data, 
but it also increases the number of parameters in the network and the computational cost of training and inference.

Stride Note: In a convolutional neural network (CNN), the stride determines the step size at which the convolutional filter is applied to the input data. 
When a stride of 1 is used, the filter is applied to adjacent input locations with no overlap. When a stride of 2 is used, the filter is applied to every other input location, 
resulting in a downsampling of the output feature map by a factor of 2 in each spatial dimension.
For example, if a convolutional layer has a stride of 2 and the input feature map is 28x28, the output feature map will be 14x14. 
This is because the filter is applied to every other input location in both the horizontal and vertical dimensions, resulting in a halving of the feature map size in each dimension.
Striding can be useful for reducing the spatial size of the feature maps and increasing the receptive field of the network, while also reducing the computational cost of the 
network by reducing the number of computations required per layer. However, it can also result in a loss of spatial resolution and details in the output feature maps.

Information about architecture config:
Tuple is structured by (filters, kernel_size, stride) 
Every conv is a same convolution. 
List is structured by "B" indicating a residual block followed by the number of repeats
"S" is for scale prediction block and computing the yolo loss
"U" is for upsampling the feature map and concatenating with a previous layer

Residual Block Note: A residual block is a building block of deep neural networks that are designed to facilitate the training of deep neural networks with many layers. 
It was introduced as part of the ResNet (Residual Network) architecture, which won the 2015 ImageNet competition.
In a residual block, the input to the block is passed through two or more layers of convolutional neural networks (CNNs), and then the output of the last layer is added to the 
original input. The resulting sum is then passed through an activation function, such as ReLU (rectified linear unit).
This process of adding the original input to the output of the convolutional layers is called shortcut connection or skip connection. 
It allows the gradient to flow directly from the input to the output, which makes it easier for the network to learn the identity function and residual functions 
(the difference between the input and output), and hence it helps in training deeper networks.
The use of residual blocks has been shown to improve the performance of deep neural networks in a variety of tasks such as image classification, object detection, and 
semantic segmentation.

Scale Note: In the context of the YOLOv3 object detection model architecture, a "scale prediction" block is a layer that predicts object detections at a specific scale of the input 
image.
Object detection models like YOLOv3 typically use feature maps generated by a series of convolutional layers to identify objects in the input image. 
However, objects of different sizes may require different scales of feature maps to be accurately detected.
To handle this, YOLOv3 uses "scale prediction" blocks at different points in the architecture to generate detection outputs at multiple scales. 
Each "scale prediction" block takes the feature map generated by the previous layer and applies a series of convolutional filters to extract features. 
It then outputs a set of bounding boxes and associated object class probabilities for each object detected at that scale.
By generating detection outputs at multiple scales, the YOLOv3 model is able to detect objects of different sizes and aspect ratios with greater accuracy.

Upsampling Note: In the context of neural networks, "upsampling" refers to the process of increasing the spatial resolution of a feature map. 
This is typically done by inserting additional pixels (or other values) between existing ones in the feature map, using techniques such as nearest-neighbor interpolation or 
bilinear interpolation.
Upsampling is often used in neural network architectures for tasks such as image segmentation or object detection, where high-resolution feature maps are required to accurately 
localize objects or boundaries. In these tasks, downsampling operations (such as pooling or strided convolutions) are often used to reduce the spatial dimensions of the feature maps 
while increasing the number of channels, which can improve the network's ability to capture high-level features. However, this also reduces the spatial resolution and can result 
in loss of detail or accuracy.
Upsampling operations are used to recover the lost spatial resolution, and to merge information from different scales or levels of abstraction in the network. In many neural network architectures, upsampling is combined with concatenation or skip connections, where the upsampled feature map is concatenated with a lower-level feature map that has been downsampled, to allow for both high-level and low-level information to be combined in the final output.
"""
config = [
    (32, 3, 1),
    (64, 3, 2),
    ["B", 1],
    (128, 3, 2),
    ["B", 2],
    (256, 3, 2),
    ["B", 8],
    (512, 3, 2),
    ["B", 8],
    (1024, 3, 2),
    ["B", 4],  # To this point is Darknet-53
    (512, 1, 1),
    (1024, 3, 1),
    "S",
    (256, 1, 1),
    "U",
    (256, 1, 1),
    (512, 3, 1),
    "S",
    (128, 1, 1),
    "U",
    (128, 1, 1),
    (256, 3, 1),
    "S",
]
# This will be used to create the model in class YOLOv3


class CNNBlock(nn.Module):
    def __init__(self, in_channels, out_channels, bn_act=True, **kwargs):
        super().__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, bias=not bn_act, **kwargs) 
        # In a convolutional neural network, the bias term is usually included in the convolutional layer to improve its ability to model the input data.
        # However, when a batch normalization layer is used after the convolution, the bias term in the convolution can be redundant and can be removed without affecting the model's performance.
        # This is because batch normalization already includes a bias term that can compensate for any biases in the convolution.
        # This explain why bias=not bn_act
        self.bn = nn.BatchNorm2d(out_channels)
        self.leaky = nn.LeakyReLU(0.1)
        self.use_bn_act = bn_act

    def forward(self, x):
        if self.use_bn_act:
            return self.leaky(self.bn(self.conv(x)))
        else:
            return self.conv(x)
        
"""
bn_act Note: Batch normalization is a technique commonly used in deep learning to improve the performance of neural networks by normalizing the inputs of each layer in the network. 
Specifically, batch normalization aims to reduce the internal covariate shift, which is a phenomenon where the distribution of the inputs to a layer changes as the parameters of the 
preceding layers are updated during training. This can make training slower and less stable.
In practice, batch normalization works by normalizing the activations of each layer in the network using the mean and standard deviation of the current minibatch of training examples.
This is done separately for each feature channel of the layer. The normalized activations are then scaled and shifted using learnable parameters, which are updated during training 
along with the other parameters of the network.
By normalizing the inputs to each layer, batch normalization can help to stabilize the training process and improve the generalization performance of the network. It has been shown to be particularly effective in deep networks, where the internal covariate shift can be a significant issue.
"""


class ResidualBlock(nn.Module):
    def __init__(self, channels, use_residual=True, num_repeats=1):
        super().__init__()
        self.layers = nn.ModuleList()
        for repeat in range(num_repeats):
            self.layers += [
                nn.Sequential(
                    CNNBlock(channels, channels // 2, kernel_size=1),
                    CNNBlock(channels // 2, channels, kernel_size=3, padding=1),
                )
            ]

        self.use_residual = use_residual
        self.num_repeats = num_repeats

    def forward(self, x):
        for layer in self.layers:
            if self.use_residual:
                x = x + layer(x)
            else:
                x = layer(x)

        return x


class ScalePrediction(nn.Module):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        self.pred = nn.Sequential(
            CNNBlock(in_channels, 2 * in_channels, kernel_size=3, padding=1),
            CNNBlock(2 * in_channels, (num_classes + 5) * 3, bn_act=False, kernel_size=1),
        )
        self.num_classes = num_classes

    def forward(self, x):
        return (
            self.pred(x)
            .reshape(x.shape[0], 3, self.num_classes + 5, x.shape[2], x.shape[3])
            .permute(0, 1, 3, 4, 2)
        )


class YOLOv3(nn.Module):
    def __init__(self, in_channels=3, num_classes=80):
        super().__init__()
        self.num_classes = num_classes
        self.in_channels = in_channels
        self.layers = self._create_conv_layers()

    def forward(self, x):
        outputs = []  # for each scale
        route_connections = []
        for layer in self.layers:
            if isinstance(layer, ScalePrediction):
                outputs.append(layer(x))
                continue

            x = layer(x)

            if isinstance(layer, ResidualBlock) and layer.num_repeats == 8:
                route_connections.append(x)

            elif isinstance(layer, nn.Upsample):
                x = torch.cat([x, route_connections[-1]], dim=1)
                route_connections.pop()

        return outputs

    def _create_conv_layers(self):
        layers = nn.ModuleList()
        in_channels = self.in_channels

        for module in config:
            if isinstance(module, tuple):
                out_channels, kernel_size, stride = module
                layers.append(
                    CNNBlock(
                        in_channels,
                        out_channels,
                        kernel_size=kernel_size,
                        stride=stride,
                        padding=1 if kernel_size == 3 else 0,
                    )
                )
                in_channels = out_channels

            elif isinstance(module, list):
                num_repeats = module[1]
                layers.append(ResidualBlock(in_channels, num_repeats=num_repeats,))

            elif isinstance(module, str):
                if module == "S":
                    layers += [
                        ResidualBlock(in_channels, use_residual=False, num_repeats=1),
                        CNNBlock(in_channels, in_channels // 2, kernel_size=1),
                        ScalePrediction(in_channels // 2, num_classes=self.num_classes),
                    ]
                    in_channels = in_channels // 2

                elif module == "U":
                    layers.append(nn.Upsample(scale_factor=2),)
                    in_channels = in_channels * 3

        return layers


if __name__ == "__main__":
    num_classes = 20
    IMAGE_SIZE = 416 # Yolo v1 uses 448 but Yolo v3 uses 416 as input size (muultiscale training)
    model = YOLOv3(num_classes=num_classes)
    x = torch.randn((2, 3, IMAGE_SIZE, IMAGE_SIZE))
    out = model(x)
    assert model(x)[0].shape == (2, 3, IMAGE_SIZE//32, IMAGE_SIZE//32, num_classes + 5)
    assert model(x)[1].shape == (2, 3, IMAGE_SIZE//16, IMAGE_SIZE//16, num_classes + 5)
    assert model(x)[2].shape == (2, 3, IMAGE_SIZE//8, IMAGE_SIZE//8, num_classes + 5)
    print("Success!")
