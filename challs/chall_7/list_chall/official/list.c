#include <ctype.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>

#define HUGE 1000
#define MIN 4

struct node {
   	int data;
   	struct node *next;
};

struct node *head = NULL;


void printList(struct node** head) {
   	struct node *ptr = *head;
   	printf("\n[ ");
	
   	while(ptr != NULL) {
      		printf("%d ",ptr->data);
      		ptr = ptr->next;
   	}
	
   	printf(" ]\n");
}


int length(struct node** head) {
	int length = 0;
	struct node *current;
		
	for(current = *head; current != NULL; current = current->next) {
		length++;
	}	
	return length;
}


bool checkIfSorted(struct node** head) {
	int l = length(head);
	if (l < 2) {
		printf("Are you kidding me???\n");
		return false;
	}
	int i;
	int prev_data = (*head)->data;
	struct node* current = (*head)->next;
	for(i = 1; i < l; i++) {
		if (prev_data > current->data) {
			printf("Nope nope!\n");
			return false;
		}
		prev_data = current->data;
		current = current->next;	
	}
	printf("Success! Congrats!!!\n");
	return true;	
}


void insertEnd(int data, struct node** head) { 

	struct node* new_node = (struct node*) malloc(sizeof(struct node)); 
	struct node *last = *head;
	new_node->data = data; 
	new_node->next = NULL; 

	if (*head == NULL) 
	{ 
		*head = new_node; 
		return; 
	} 

	while (last->next != NULL) 
		last = last->next; 

	last->next = new_node; 
	return;	 
} 


bool isEmpty() {
   	return head == NULL;
}


void reverse(struct node** head_ref) {
   	struct node* prev   = NULL;
   	struct node* current = *head_ref;
   	struct node* next;
	
   	while (current != NULL) {
      		next  = current->next;
      		current->next = prev;   
      		prev = current;
      		current = next;
   	}
	
   	*head_ref = prev;
}


int sum(struct node** head_ref) {
	int res = 0;
	struct node* prev = NULL;
	struct node* current = *head_ref;
	struct node* next;

	while (current != NULL) {
		res += current->data;
		current = current->next;
	}
	return res;
}

// Returns true if s is a number else false
bool isNumber(char* s) 
{ 
	int length = strlen(s);
	for (int i = 0; i < length; i++) 
		if (isdigit(s[i]) == false) 
			return false; 
	return true; 
} 


void initList(int start, int end, char* argv[]) {
	int index;
	for (index = start; index < end; index++) {
		if (isNumber(argv[index])) {
			int value = atoi(argv[index]);
			insertEnd(value, &head);
		}
	}
}


void setup(int start, int end, char* argv[]) {
	initList(start, end, argv);
	if (isEmpty()) {
		printf("Error\n");
		exit(-1);
	}
}

void sumCase(int start, int end, char* argv[]) {
	setup(start, end, argv);
	int s = sum(&head);
	printf("%d\n", s);
	if (s > HUGE)
		printf("Wow!!! What a huge number..\n");
}


void sortCase(int start, int end, char* argv[]) {
	setup(start, end, argv);
	int len = length(&head);
	if (len < MIN) {
		printf("Not enough\n");
		exit(-1);
	}
	checkIfSorted(&head);
	printList(&head);
}


void reverseCase(int start, int end, char* argv[]) {
	setup(start, end, argv);
	reverse(&head);
	printList(&head);
}


void main(int argc, char* argv[]) {
	if (argc < 2) {
		printf("Not enough arguments\n");
		return;
	}
	int c;
	while ((c = getopt(argc, argv, "asr")) != -1) {	
		switch(c) {
			case 'a':
				sumCase(optind, argc, argv);
				return;

			case 's':
				sortCase(optind, argc, argv);	
				return;

			case 'r':
				reverseCase(optind, argc, argv);	
				return;

			default:
				printf("Incorrect option\n");
				return;
		}
	}
	
 	return;	
}


