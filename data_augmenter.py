from __future__ import annotations
from logic.code_data import CodeData
from logic.text_data import TextData
from logic.text_code_data import TextCodeData

import os, yaml, time, argparse, warnings
import transformations.text.utils.initialize as text_helper

def get_argparser() -> argparse.ArgumentParser:
    """
    Get the configured argument parser
    """

    parser = argparse.ArgumentParser(description='Augment text and code data from CSV file')
    parser.add_argument('--output-filepath', '-o',
                        metavar='FILEPATH',
                        dest='output',
                        required=False,
                        type=str,
                        default='output.csv',
                        help='Output filepath where to store the CSV file')
    parser.add_argument('--workers', '-w',
                        metavar='N_WORKERS',
                        dest='workers',
                        required=False,
                        type=int,
                        default=1,
                        help='Number of threads to be used during the process. Default value = 1')
    parser.add_argument('--chunk-size', '-cs',
                        metavar='C_SIZE',
                        dest='chunk_size',
                        required=False,
                        type=int,
                        default=1,
                        help='Size of the portion of the dataset to be processed by each thread.. Default value = 100')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        dest='verbose',
                        required=False,
                        default=False,
                        help='If selected it shows some code execution messages on the screen')


    required = parser.add_argument_group('required arguments')
    required.add_argument('--input-file', '-i',
                        metavar='FILEPATH',
                        dest='data_filepath',
                        required=True,
                        type=str,
                        help='The CSV filepath where to retrieve the data to augment.')
    
    required.add_argument('--type', '-t',
                        metavar='TYPE',
                        dest='type',
                        required=True,
                        choices={"text", "code", "text-code"},
                        default="text",
                        type=str,
                        help='Select the type of augmentation to perform. Possible choices: \'text\', \'code\' or \'text-code\'"')
                        
    return parser


if __name__ == '__main__':    
    warnings.filterwarnings("ignore")
    
    # Read arg parameters
    parser = get_argparser()
    args = parser.parse_args()
    
    # Read csv
    filepath = args.data_filepath
    if not os.path.isfile(filepath):
        print('Input file not found. Enter the path of the CSV file containing the data to be augmented.')
        exit()
    
    # Load config file
    if not os.path.isfile(filepath):
        print('File \'config.yaml\' not found. Please insert the config file under the root directory.')
        exit()
        
    with open('config.yaml', 'r') as file:
        yml = yaml.safe_load(file)
    
    # Retrieve active rules
    txt_yml, code_yml = yml['text'], yml['code']
    start_time = time.time()
    
    print(f'Augmenting the dataset located on {filepath} ...')
    
    if args.type == 'text':
        text_helper.initialize_models()
        data = TextData(filepath, txt_yml, verbose=args.verbose)
    elif args.type == 'code':
        data = CodeData(filepath, code_yml, verbose=args.verbose)
    elif args.type == 'text-code':
        text_helper.initialize_models()
        data = TextCodeData(filepath, yml, verbose=args.verbose)
      
    data.compute(out_fp = args.output, workers = args.workers, chunk_size = args.chunk_size)
    
    print(f'Total execution time: {time.time() - start_time}')
    print(f'Dataset augmented successfully. You can find the new dataset at the following location: {args.output} .')
    