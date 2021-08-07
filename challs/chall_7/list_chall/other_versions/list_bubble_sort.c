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


bool listCompare(struct node** head1, struct node** head2) {
	int l1 = length(head1);
	int l2 = length(head2);
	if (l1 != l2)
		return false;
	int i;
	struct node* current1 = *head1;
	struct node* current2 = *head2;
	for (i = 0; i < l1; i++) {
		if (current1->data != current2->data)
			return false;
		current1 = current1->next;
		current2 = current2->next;
	}
	return true;
}


void insertFirst(int data, struct node** head) {

   struct node *link = (struct node*) malloc(sizeof(struct node));
	
   link->data = data;
   link->next = *head;
   *head = link;
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


struct node* deleteFirst() {
   struct node *tempLink = head;
   head = head->next;
   return tempLink;
}


bool isEmpty() {
   return head == NULL;
}


struct node* copyListByValue() {
	struct node *new_head = NULL;
	struct node* current;

	for (current = head; current != NULL; current = current->next) {
		insertEnd(current->data, &new_head);
	}
	return new_head;
}

struct node* delete(int data) {

   struct node* current = head;
   struct node* previous = NULL;
	
   if(head == NULL) {
      return NULL;
   }

   while(current->data != data) {

      if(current->next == NULL) {
         return NULL;
      } else {
         previous = current;
         current = current->next;
      }
   }


   if(current == head) {

      head = head->next;
   } else {
      previous->next = current->next;
   }    
	
   return current;
}


/*
 * Merge sort: for future experiments


struct node* sortedMerge(struct node* a, struct node* b) {
	if (a == NULL)
		return b;

	else if (b == NULL)
		return a;

	struct node* result = NULL;

	if (a->data <= b->data) {
		result = a;
		result->next = sortedMerge(a->next, b);
	}
	else {
		result = b;
		result->next = sortedMerge(a, b->next);
	}

	return result;
}


void FrontBackSplit(struct node* source, struct node** frontRef,
					struct node** backRef) {
	if (source == NULL || source->next == NULL) {
		*frontRef = source;
		*backRef = NULL;
		return;
	}

	struct node* slow = source;
	struct node* fast = source->next;

	while (fast != NULL) {
		fast = fast->next;
		if (fast != NULL)
		{
			slow = slow->next;
			fast = fast->next;
		}
	}
	*frontRef = source;
	*backRef = slow->next;
	slow->next = NULL;
}


void mergeSort(struct node** head) {
	if (*head == NULL || (*head)->next == NULL)
		return;

	struct node* a;
	struct node* b;

	FrontBackSplit(*head, &a, &b);

	mergeSort(&a);
	mergeSort(&b);

	*head = sortedMerge(a, b);
}
*/


// Bubble sort
void bubbleSort(struct node** head_ref) {

   int i, j, k, tempKey, tempData;
   struct node *current;
   struct node *next;
	
   int size = length(head_ref);
   k = size ;
	
   for ( i = 0 ; i < size - 1 ; i++, k-- ) {
      current = *head_ref;
      next = (*head_ref)->next;
		
      for ( j = 1 ; j < k ; j++ ) {   

         if ( current->data > next->data ) {
            tempData = current->data;
            current->data = next->data;
            next->data = tempData;
         }
			
         current = current->next;
         next = next->next;
      }
   }   
}
// End of Bubble sort


void doSort() {
	bubbleSort(&head);
}
// End of Merge Sort 


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


void check(struct node* original_head, struct node* head_after_sorting) {
	bool res = listCompare(&original_head, &head_after_sorting);
	if (res)
		printf("Success !!! Congrats\n");
	else
		printf("MMhmh\n");
}

void sortCase(int start, int end, char* argv[]) {
	setup(start, end, argv);
	struct node* original_head = copyListByValue();
	doSort();
	int len = length(&head);
	if (len < MIN) {
		printf("Not enough\n");
		exit(-1);
	}
	check(original_head, head);
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


