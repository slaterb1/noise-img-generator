import argparse
import png
import random
import numpy as np
from perlin import PerlinNoiseFactory

def normalize(p, new_max):
    absolute_max = 0
    absolute_min = 255
    for row in range(len(p)):
        cur_max = max(p[row])
        cur_min = min(p[row])
        if cur_max > absolute_max:
            absolute_max = cur_max
        if cur_min < absolute_min:
            absolute_min = cur_min

    for row in range(len(p)):
        for col in range(len(p[row])):
            p[row][col] = round((p[row][col] - absolute_min) / (absolute_max - absolute_min) * new_max)

    return p

def write_noise(p, size, filename):
    w = png.Writer(size, size, greyscale=True)
    f = open(filename, 'wb')
    w.write(f, p)
    f.close()

def random_noise(size, cluster, imgs, norms):
    # generate random image matrix
    p = [[random.randint(0, 255) for c in range(size)] for r in range(size)]

    # sum multiple random images to create larger groups
    for img in range(imgs - 1):
        if (img + 1) % 5 == 0:
            print('generating image:', img + 1)
        img = [[random.randint(0, 255) for c in range(size)] for r in range(size)]
        for row in range(len(p)):
            for col in range(len(p[row])):
                p[row][col] += img[row][col]

    # avg pixels in clusters to form larger groups
    if cluster:
        if size % cluster != 0:
            raise Exception('Size must be evenly divisable by cluster size!')

        for row in range(0, len(p), cluster):
            for col in range(0, len(p[0]), cluster):
                # compute avg within subset
                sum_value = 0
                for offset in range(cluster):
                    sum_value = sum_value + np.sum(p[row + offset][col:col + cluster])
                avg_value = round(sum_value / (cluster * cluster))

                # update all values to use average
                for row_offset in range(cluster):
                    for col_offset in range(cluster):
                        p[row + row_offset][col + col_offset] = avg_value

    # normalize values to increase range
    for norm in range(norms):
        p = normalize(p, 255)

    return p

def perlin_noise(size, dimensions, octaves, tile):
    pnf = PerlinNoiseFactory(dimensions, octaves, tile)
    p = [[pnf(row / size, col/size) for col in range(size)] for row in range(size)]
    p = normalize(p, 255)
    return p


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='Generate noise png files.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--gentype', type=str, default='random',
                        help='specify a noise generator to use [random, perlin]')
    parser.add_argument('--size', type=int, default=512,
                        help='size of output image')
    parser.add_argument('--filename', type=str, default='noise.png',
                        help='name of file created')
    parser.add_argument('--seed', type=int, default=None,
                        help='seed to use for generation')
    parser.add_argument('--cluster', type=int, default=0,
                        help='width of kernal to average neighbouring pixels')
    parser.add_argument('--imgs', type=int, default=1,
                        help='number of random generated images to combine')
    parser.add_argument('--norms', type=int, default=1,
                        help='number of times to normalize image')
    parser.add_argument('--dims', type=int, default=2,
                        help='number of dimensions to use with perlin')
    parser.add_argument('--octaves', type=int, default=1,
                        help='number of octaves to use with perlin, recommended max 4')
    parser.add_argument('--tile', nargs='+', type=int, default=[1,1],
                        help='connected tilings to be used [space dimensions]')

    args = parser.parse_args()

    random.seed(args.seed) # set seed if included
    # Implement specified noise generator
    if args.gentype == 'random':
        noise = random_noise(args.size, args.cluster, args.imgs, args.norms)
    elif args.gentype == 'perlin':
        noise = perlin_noise(args.size, args.dims, args.octaves, tuple(args.tile))
    else:
        raise ValueError('Noise generator "{0}" does not exist. Run --help to see supported generators.'.format(args.gentype))

    # Write noise to file
    write_noise(noise, args.size, args.filename)
