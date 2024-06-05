"""
6.101 Lab 2:
Image Processing 2
"""

#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# code from last lab below


def get_pixel(image, row, col, boundary="extend"):
    """Get a pixel's value given its location."""

    def out_of_bounds(image, row, col):
        """Will check if a pixel is out of bounds.
        Returns True if it is"""

        if row < 0 or col < 0:
            return True
        return row >= image["height"] or col >= image["width"]

    # inbound pixels, just return value
    if not out_of_bounds(image, row, col):
        form = row * image["width"] + col
        return image["pixels"][form]

    # now entering code for out of bounds pixels

    # every out of bounds pixel becomes 0
    if boundary == "zero":
        return 0

    # extend last known pixels from rows/columns
    if boundary == "extend":
        row = max(row, 0)
        if row >= image["height"]:
            row = image["height"] - 1
        col = max(col, 0)
        if col >= image["width"]:
            col = image["width"] - 1
        form = row * image["width"] + col
        return image["pixels"][form]

    # wrap out of bounds pixels
    if boundary == "wrap":
        if row < 0:
            row = row % image["height"]
        if row >= image["height"]:
            row = row % image["height"]
        if col < 0:
            col = col % image["width"]
        if col >= image["width"]:
            col = col % image["width"]
        form = row * image["width"] + col
        return image["pixels"][form]


def set_pixel(image, row, col, color):
    """Change a pixel's value given its location."""

    # formuala to get pixel index
    form = row * image["width"] + col
    # change color/pixel value
    image["pixels"][form] = color


def apply_per_pixel(image, func):
    """Will apply a filter to an image."""

    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": [],
    }

    for pix in image["pixels"]:
        result["pixels"].append(pix)

    for row in range(image["height"]):
        for col in range(image["width"]):
            # use og color to get new color
            color = get_pixel(image, row, col)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE:
    The kernal is just a list of numbers
    """
    poss_bounds = ["zero", "extend", "wrap"]
    if boundary_behavior not in poss_bounds:
        return None

    def linear_combination(kernel, row, col):
        """Will return the new color value after applying the
        kernel to a specific pixel. Row and col are the location of the
        centered pixel. Pixel is the dictionary of image pixels."""

        # how far you can go from centered pixel
        offset = int((len(kernel) ** (1 / 2)) // 2)

        combined = []
        count = 0
        # get the relevant locations
        for numb in range(-offset, offset + 1):
            for num in range(-offset, offset + 1):
                color = get_pixel(image, row + numb, col + num)
                combined.append(color * kernel[count])
                count += 1
        return sum(combined)

    # from apply per pixel
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }

    # now use function to get the new pixel values
    for row in range(image["height"]):
        for col in range(image["width"]):
            # use og color to get new color
            new_color = linear_combination(kernel, row, col)
            set_pixel(result, row, col, new_color)

    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
    }

    # identify pixels that need to be clipped and do so
    clipped = []
    for pix in image["pixels"]:
        pixel = round(pix)
        if pixel > 255:
            clipped.append(255)
            continue
        if pixel < 0:
            clipped.append(0)
            continue
        else:
            clipped.append(pixel)

    result["pixels"] = clipped
    return result


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """

    def n_by_n_kernel(n):
        """function that takes a single argument n and returns an n-by-n
        box blur kernel."""

        kern_len = n**2
        individ_val = 1 / kern_len
        kernel = []
        for num in range(kern_len):
            kernel.append(individ_val)
        return kernel

    blur = n_by_n_kernel(kernel_size)

    return round_and_clip_image(correlate(image, blur, "extend"))


def sharpened(image, n):
    """image is an image and n denotes the size of the blur
    kernel that should be used to generate the blurred copy of the image.

    Will subtract an "unsharp" (blurred) version of the image from a scaled
      ersion of the original image."""

    blur = blurred(image, n)
    scaled = apply_per_pixel(image, lambda x: 2 * x)
    sharp = []
    for ind in range(len(blur["pixels"])):
        sharp.append(scaled["pixels"][ind] - blur["pixels"][ind])

    return round_and_clip_image(
        {"height": image["height"], "width": image["width"], "pixels": sharp}
    )


def edges(image):
    """Takes and image and implements a filter that detects
    edges in images."""

    kern1 = [-1, -2, -1, 0, 0, 0, 1, 2, 1]
    kern2 = [-1, 0, 1, -2, 0, 2, -1, 0, 1]

    output1 = correlate(image, kern1, "extend")
    output2 = correlate(image, kern2, "extend")

    final = []

    for ind in range(len(output1["pixels"])):
        add = output1["pixels"][ind] ** 2 + output2["pixels"][ind] ** 2
        out = add ** (1 / 2)
        final.append(out)

    result = {"height": image["height"], "width": image["width"], "pixels": final}
    return round_and_clip_image(result)


# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    # image is  greyscale filter

    # split color image into 3 different greyscale images
    def color_split(color):
        """Will split a color image into 3 different greyscale images.
        Image is a dictionary. Returns a list"""

        red = []
        green = []
        blue = []
        for tup in color["pixels"]:
            red.append(tup[0])
            green.append(tup[1])
            blue.append(tup[2])

        red_grey = {"height": color["height"], "width": color["width"], "pixels": red}
        green_grey = {
            "height": color["height"],
            "width": color["width"],
            "pixels": green,
        }
        blue_grey = {"height": color["height"], "width": color["width"], "pixels": blue}

        return [red_grey, green_grey, blue_grey]

    # combine color images into
    def color_combine(grey_list):
        """Will combine three greyscale images into a single new color image.
        Takes an input in the same form that color_split returns. A list in order
        of r,g,b grey images."""

        color_tuples = []

        for n in range(len(grey_list[0]["pixels"])):
            tup = (
                grey_list[0]["pixels"][n],
                grey_list[1]["pixels"][n],
                grey_list[2]["pixels"][n],
            )
            color_tuples.append(tup)

        return {
            "height": grey_list[0]["height"],
            "width": grey_list[0]["width"],
            "pixels": color_tuples,
        }

    def color_filter(color):
        """Function that takes a color image as input and returns a filtered
        color image."""
        # make list of greyscale images
        rgb_list = color_split(color)
        filtered = []
        # run greyscale filter on each
        for img in rgb_list:
            filtered.append(filt(img))

        return color_combine(filtered)

    return color_filter


def make_blur_filter(kernel_size):
    """Just make a function that creates a function
    to run blurred when given a kernel size."""

    def blur_filter(image):
        return blurred(image, kernel_size)

    return blur_filter


def make_sharpen_filter(kernel_size):
    """Just make a function that creates a function
    to run sharpened when given a kernel size. Same methodology
    as make_blur_filter"""

    def sharpen_filter(image):
        return sharpened(image, kernel_size)

    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def cascade(image):
        """Given an image and a list of filters, will apply each of those filters
        in order."""

        image_copy = {
            "height": image["height"],
            "width": image["width"],
            "pixels": image["pixels"].copy(),
        }

        # all filters are assumed to be of one type
        for n in range(len(filters)):
            image_copy = filters[n](image_copy)
        return image_copy

    return cascade


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    raise NotImplementedError


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    # formula to get grep pixel from rgb values below

    color = {"height": image["height"], "width": image["width"], "pixels": []}
    # calculate every greyscale pixels suing given formula and color rgb tuple
    for tup in image["pixels"]:
        r, g, b = tup[0], tup[1], tup[2]
        # formula to get grep pixel from rgb values below
        grey = round(0.299 * r + 0.587 * g + 0.114 * b)
        color["pixels"].append(grey)

    return color


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


# def cumulative_energy_map(energy):
#     """
#     Given a measure of energy (e.g., the output of the compute_energy
#     function), computes a "cumulative energy map" as described in the lab 2
#     writeup.

#     Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
#     the values in the 'pixels' array may not necessarily be in the range [0,
#     255].
#     """
    
#     cumulative = {"width": energy["width"], "height": energy["height"], "pixels": []}

#     # first row stays the same
#     for pix in energy["pixels"][: energy["width"]]:
#         cumulative["pixels"].append(pix)

#     # for every pixel not in the first row
#     for ind in range(len(energy["pixels"][energy["width"] :])):
#         og = energy["pixels"][ind]
#         # calculate the min of the adjacent pixels
#         adj = []
#         diff = [-1, 0, 1]
#         for num in diff:
#             # adjacent index
#             neigh = ind - energy["width"] + num
#             # cumulative value
#             adj.append(energy["pixels"][neigh])
#             # print(adj, 'ADJ')
#         # now add the minimum adjacent value to the original, and then to pixels
#         cumulative["pixels"].append(og + min(adj))

#     return cumulative


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    raise NotImplementedError


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    raise NotImplementedError


# custon filter


def custom_feature(image):
    """Will give an image a 'ghostly' effect!"""
    new = filter_cascade([inverted, make_sharpen_filter(3)])
    return round_and_clip_image(new(image))


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """

    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # inverted_color = color_filter_from_greyscale_filter(inverted)
    # cat = load_color_image('cat.png')
    # inverted_cat = inverted_color(cat)
    # # print(inverted_cat, 'inverted cat')
    # save_color_image(inverted_cat, 'inverted_cat.png')
    # blure = make_blur_filter(9)
    # color_blur = color_filter_from_greyscale_filter(blure)
    # py = load_color_image('python.png')
    # blur_pyth = color_blur(py)
    # save_color_image(blur_pyth, 'blur_pyth.png')
    # sharp = make_sharpen_filter(7)
    # color_sharp = color_filter_from_greyscale_filter(sharp)
    # sparchi = load_color_image('sparrowchick.png')
    # sharp_sparchi = color_sharp(sparchi)
    # save_color_image(sharp_sparchi, 'sharp_sparchi.png')
    # frog = load_color_image("frog.png")

    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])

    # frog_cascade = filt(frog, [filter1, filter1, filter2, filter1])
    # save_color_image(frog_cascade, 'frog_cascade3.png')

    map = {
        "width": 9,
        "height": 4,
        "pixels": [
            160,
            160,
            0,
            28,
            0,
            28,
            0,
            160,
            160,
            255,
            218,
            10,
            22,
            14,
            22,
            10,
            218,
            255,
            255,
            255,
            30,
            0,
            14,
            0,
            30,
            255,
            255,
            255,
            255,
            31,
            22,
            0,
            22,
            31,
            255,
            255,
        ],
    }
    # print(cumulative_energy_map(result) == {'width': 9, 'height': 4, 'pixels': [160, 160, 0, 28, 0, 28, 0, 160, 160, 415, 218, 10, 22, 14, 22, 10, 218, 415, 473, 265, 40, 10, 28, 10, 40, 265, 473, 520, 295, 41, 32, 10, 32, 41, 295, 520]})
    # print(cumulative_energy_map(map))



    # ghost = load_color_image('ghost.png')
    # spider = load_color_image('spider.png')
    # color_invert, color_sharp = color_filter_from_greyscale_filter(inverted), color_filter_from_greyscale_filter(make_sharpen_filter(3))
    
    # filt = color_filter_from_greyscale_filter(ghostly)
    # filt_spider = filt(spider)
    
    
    # save_color_image(filt_spider, 'filt_spider.png')
    # flood = load_color_image('flood_input.png')
    # print(flood['width'], flood['height'])
    afik = load_color_image('afik.png')
    color = color_filter_from_greyscale_filter(make_sharpen_filter(2))
    new = color(afik)
    save_color_image(new, 'sharp_afik.png')
    # unaltered = [160, 160, 0, 28, 0, 28, 0, 160, 160, 255, 218, 10, 22, 14, 22, 10, 218, 255, 255, 255, 30, 0, 14, 0, 30, 255, 255, 255, 255, 31, 22, 0, 22, 31, 255, 255]
    # got = [160, 160, 0, 28, 0, 28, 0, 160, 160, 415, 191, 22, 28, 0, 28, 22, 191, 320, 415, 218, 10, 22, 14, 22, 10, 218, 415, 415, 265, 40, 10, 28, 10, 40, 265, 473]
    # want = [160, 160, 0, 28, 0, 28, 0, 160, 160, 415, 218, 10, 22, 14, 22, 10, 218, 415, 473, 265, 40, 10, 28, 10, 40, 265, 473, 520, 295, 41, 32, 10, 32, 41, 295, 520]
    