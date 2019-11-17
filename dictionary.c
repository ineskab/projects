// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Represents a hash table
node *hashtable[N];

// Create a global variable for storing number of words in the dictionary
long WORD_COUNT = 0;

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {
        // allocate memory for the new node
        node *newptr = malloc(sizeof(node));

        // chec that memory was succesfully created for the node; if not free memory
        if (newptr == NULL)
        {
            unload();
            WORD_COUNT = 0;
            return false;
        }

        // insert the word into the struct
        strcpy(newptr->word, word);
        newptr -> next = NULL;
        WORD_COUNT++;
        // get the index for the word from the hash function
        unsigned int index = hash(word);

        if (hashtable[index] == NULL)
        {
            hashtable[index] = newptr;
        }
        else
        {
            // new node to point at the first node located in the hashtable under the index
            newptr -> next = hashtable[index];
            // replace at first postition the current newptr
            hashtable[index] = newptr;
        }

    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    if (WORD_COUNT > 0)
    {
        return WORD_COUNT;
    }
    else
    {
        return 0;
    }
}
// Returns true if word is in dictionary else false
bool check(const char *word)
{
    int index = hash(word);
    node *current_pointer = hashtable[index];

    while (current_pointer != NULL)
    {
        // check the word in current node
        char *current_word = current_pointer -> word;

        if (strcasecmp(word, current_word) == 0)
        {
            return true;
        }
        current_pointer = current_pointer -> next;

    }
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    if (WORD_COUNT == 0)
    {
        return false;
    }

    for (int i = 0; i < N; i++)
    {
        node *current_pointer = hashtable[i];
        while (current_pointer != NULL)
        {
            node *next_pointer = current_pointer -> next;

            // free current node
            free(current_pointer);
            current_pointer = next_pointer;
        }
    }
    return true;
}
